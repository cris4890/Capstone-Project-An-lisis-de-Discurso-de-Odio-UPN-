"""Entrenamiento y evaluación por ejecución; nunca sobrescribe resultados anteriores."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import random
import subprocess
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.metrics import f1_score, ConfusionMatrixDisplay

from corpus import prepare_corpus, validate_manifest
from data_pipeline import generate_synthetic_data
from experiment import CLASSES, split_corpus, select_model, metrics_for, bootstrap_intervals, subgroup_metrics
from model_classes import RuleBasedClassifier, TransformerClassifier

ROOT = Path(__file__).resolve().parent


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def run_training_pipeline(data_path=None, output=None, include_transformer=False,
                          epochs=3, bootstrap_samples=500, manifest_path=None, annotation_db=None):
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if epochs < 1 or bootstrap_samples < 1:
        raise ValueError("Épocas y remuestreos deben ser positivos.")
    out = Path(output) if output else ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if out.exists():
        raise FileExistsError("La ejecución ya existe; elija una carpeta nueva.")
    if data_path is None:
        frame, quality = prepare_corpus(generate_synthetic_data())
        source_hash = None
    else:
        data_path = Path(data_path)
        frame = pd.read_csv(data_path)
        source_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if "origen" not in frame or frame.origen.isna().any() or frame.origen.nunique() != 1 or not set(frame.origen).issubset({"sintetico", "reddit_autorizado", "licenciado"}):
            raise ValueError("Declare una única procedencia para el corpus.")
        quality = {"origin": frame.origen.iloc[0]}
        if frame.origen.iloc[0] != "sintetico":
            if not manifest_path or not annotation_db:
                raise ValueError("Datos reales requieren --manifest y --annotation-db.")
            manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
            quality["authorization_evidence_sha256"] = validate_manifest(manifest)
            if "fecha" not in frame:
                raise ValueError("Faltan fechas del corpus real.")
            dates = pd.to_datetime(frame.fecha, utc=True, errors="coerce")
            if dates.isna().any() or not dates.between(pd.to_datetime(manifest["fecha_inicio"], utc=True), pd.to_datetime(manifest["fecha_fin"], utc=True)).all():
                raise ValueError("El corpus contiene fechas fuera del periodo autorizado.")
            from annotations import AnnotationStore
            frame = AnnotationStore(annotation_db).export(source_hash, frame)
    # Exportar solo columnas analíticas; nunca copiar originales a las ejecuciones.
    from corpus import SAFE_COLUMNS
    frame = frame[[c for c in SAFE_COLUMNS if c in frame]].copy()
    from data_pipeline import clean_and_anonymize
    for column in ["texto_limpio", "justificacion", "grupo_objetivo"]:
        if column in frame:
            frame[column] = frame[column].apply(clean_and_anonymize)
    splits = split_corpus(frame, seed)
    out.mkdir(parents=True)
    frame.to_csv(out / "corpus.csv", index=False)
    split_manifest = pd.concat([part[["id_comentario", "id_hilo"]].assign(partition=name) for name, part in splits.items()])
    split_manifest.to_csv(out / "partitions.csv", index=False)
    train, val, test = [splits[name] for name in ["train", "validation", "test"]]
    candidates = {
        "baseline": RuleBasedClassifier(),
        "logistic": make_pipeline(TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, strip_accents="unicode"),
                                  LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed)),
        "svm": make_pipeline(TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, strip_accents="unicode"),
                             LinearSVC(class_weight="balanced", C=.8, max_iter=2000, random_state=seed))}
    names = {"baseline": "Línea base de reglas", "logistic": "TF-IDF + LogisticRegression", "svm": "TF-IDF + LinearSVC"}
    validation_scores, training_seconds = {}, {}
    for key, model in candidates.items():
        start = time.perf_counter()
        model.fit(train.texto_limpio, train.etiqueta)
        training_seconds[key] = time.perf_counter()-start
        validation_scores[key] = float(f1_score(val.etiqueta, model.predict(val.texto_limpio), labels=CLASSES, average="macro", zero_division=0))
    if include_transformer:
        model = TransformerClassifier(num_epochs=epochs, batch_size=4, lr=2e-5)
        start = time.perf_counter()
        model.fit(train.texto_limpio, train.etiqueta, val.texto_limpio, val.etiqueta)
        training_seconds["transformer"] = time.perf_counter()-start
        candidates["transformer"] = model
        names["transformer"] = "Transformer XLM-RoBERTa multilingüe"
        validation_scores["transformer"] = float(f1_score(val.etiqueta, model.predict(val.texto_limpio), labels=CLASSES, average="macro", zero_division=0))
    # La identidad del seleccionado queda fijada ANTES de cualquier inferencia de prueba.
    selected = select_model(validation_scores)
    write_json(out / "selection.json", {"criterion": "validation_macro_f1", "selected_model": selected, "scores": validation_scores})
    entries, results = {}, []
    functional = pd.read_csv(ROOT / "tests" / "functional_cases.csv")
    from data_pipeline import clean_and_anonymize
    functional["text"] = functional.text.apply(clean_and_anonymize)
    for key, model in candidates.items():
        artifact = f"{key}.pkl"
        kind = "joblib"
        if key == "transformer":
            artifact, kind = "transformer", "transformer"
            model.save(out / artifact)
        else:
            joblib.dump(model, out / artifact)
        entries[key] = {"name": names[key], "kind": kind, "artifact": artifact}
        tracemalloc.start()
        start = time.perf_counter()
        predictions = model.predict(test.texto_limpio)
        seconds = time.perf_counter()-start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result = metrics_for(test.etiqueta, predictions)
        result.update({"key": key, "model_name": names[key], "validation_macro_f1": validation_scores[key],
                       "training_seconds": training_seconds[key], "inference_seconds": seconds,
                       "latency_ms_per_text": seconds / len(test) * 1000,
                       "texts_per_second": len(test)/seconds if seconds else None,
                       "python_peak_bytes": peak, "memory_scope": "Python allocations only; excludes native tensors and GPU",
                       "bootstrap_95": bootstrap_intervals(test, predictions, bootstrap_samples),
                       "subgroups": subgroup_metrics(test, predictions)})
        result.update({"precision_odio": result["per_class"]["Odio"]["precision"],
                       "recall_odio": result["per_class"]["Odio"]["recall"],
                       "fnr_odio": result["per_class"]["Odio"]["fnr"]})
        for label in CLASSES:
            result["f1_" + label.lower()] = result["per_class"][label]["f1"]
        record = test[["id_comentario", "id_hilo", "subreddit", "idioma", "tipo_contenido", "etiqueta"]].copy()
        record["prediction"] = predictions
        record["correct"] = record.etiqueta == predictions
        record.to_csv(out / f"predictions_{key}.csv", index=False)
        record[~record.correct].to_csv(out / f"errors_{key}.csv", index=False)
        ConfusionMatrixDisplay(np.asarray(result["confusion_matrix"]), display_labels=CLASSES).plot()
        plt.tight_layout()
        plt.savefig(out / f"matrix_{key}.png")
        plt.close()
        cases = functional.copy()
        cases["prediction"] = model.predict(cases.text)
        cases["correct"] = cases.expected == cases.prediction
        cases.to_csv(out / f"functional_{key}.csv", index=False)
        result["functional"] = {"n": len(cases), "accuracy": float(cases.correct.mean()),
                                "by_category": cases.groupby("category").correct.mean().to_dict()}
        results.append(result)
    packages = {dist.metadata["Name"]: dist.version for dist in importlib.metadata.distributions() if dist.metadata["Name"]}
    (out / "requirements.lock.txt").write_text("\n".join(f"{k}=={v}" for k,v in sorted(packages.items())), encoding="utf-8")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, "unknown"
    source_files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob("*.py")}
    report = {"schema_version": 2, "created_at": datetime.now(timezone.utc).isoformat(),
              "origin": frame.origen.iloc[0], "quality": quality, "source_sha256": source_hash,
              "corpus_sha256": hashlib.sha256((out/"corpus.csv").read_bytes()).hexdigest(),
              "seed": seed, "git_commit": commit, "git_dirty": bool(dirty), "source_sha256_by_file": source_files,
              "python": platform.python_version(), "platform": platform.platform(),
              "split_sizes": {k: len(v) for k,v in splits.items()}, "test_partition_size": len(test),
              "selection_criterion": "validation_macro_f1", "selected_model": selected,
              "transformer_included": include_transformer, "models": entries, "results": results,
              "limitations": ["Corpus sintético: no estima prevalencia en Reddit." if frame.origen.iloc[0] == "sintetico" else "Revisar representatividad del muestreo.",
                              "Probabilidades no calibradas; requieren revisión humana.",
                              "Los intervalos son exploratorios con muestras pequeñas."]}
    write_json(out / "run.json", report)
    print(f"Ejecución completa: {out.resolve()}")
    print(f"Seleccionado por validación: {names[selected]}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data")
    parser.add_argument("--output")
    parser.add_argument("--include-transformer", action="store_true")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--manifest")
    parser.add_argument("--annotation-db")
    args = parser.parse_args()
    run_training_pipeline(args.data, args.output, args.include_transformer, args.epochs, args.bootstrap, args.manifest, args.annotation_db)
