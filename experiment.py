"""Particiones por hilo y evaluación reproducible sin selección sobre prueba."""
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, confusion_matrix,
                             precision_recall_fscore_support, f1_score)

CLASSES = ["Odio", "Ofensivo", "Neutro"]


def split_corpus(df, seed=42):
    required = {"id_comentario", "id_hilo", "texto_limpio", "etiqueta", "idioma", "subreddit", "tipo_contenido"}
    if required - set(df):
        raise ValueError("Faltan campos para separar por hilo: " + str(required - set(df)))
    if df[list(required)].isna().any().any() or df.id_comentario.duplicated().any():
        raise ValueError("Hay campos vacíos o identificadores repetidos.")
    if df[list(required)].astype(str).apply(lambda c: c.str.strip()).eq("").any().any():
        raise ValueError("Hay metadatos o textos vacíos.")
    if not set(df.idioma).issubset({"es", "en"}):
        raise ValueError("El corpus debe contener solamente español e inglés revisados.")
    if set(df.etiqueta) != set(CLASSES):
        raise ValueError("Se requieren las tres clases anotadas.")
    if df.texto_limpio.duplicated().any():
        raise ValueError("Elimine textos duplicados antes de separar por hilo.")
    if "revision_idioma" in df and df.revision_idioma.astype(str).str.lower().isin(["true", "1"]).any():
        raise ValueError("Resuelva la revisión de idioma antes de entrenar.")

    def partition(frame, fraction, state):
        splitter = GroupShuffleSplit(n_splits=200, test_size=fraction, random_state=state)
        best = None
        for left, right in splitter.split(frame, groups=frame.id_hilo):
            if any(set(frame.iloc[idx].etiqueta) != set(CLASSES) for idx in (left, right)):
                continue
            score = abs(len(right) / len(frame) - fraction)
            for col in ["etiqueta", "idioma", "subreddit", "tipo_contenido"]:
                target = frame[col].value_counts(normalize=True)
                for idx in (left, right):
                    observed = frame.iloc[idx][col].value_counts(normalize=True).reindex(target.index, fill_value=0)
                    score += float((observed - target).abs().sum())
            if best is None or score < best[0]:
                best = (score, left, right)
        if best is None:
            raise ValueError("No hay suficientes hilos y clases para formar tres particiones; amplíe el corpus.")
        return frame.iloc[best[1]].copy(), frame.iloc[best[2]].copy()

    train, temporary = partition(df, .30, seed)
    val, test = partition(temporary, .50, seed + 1)
    return {"train": train, "validation": val, "test": test}


def select_model(validation_scores):
    if not validation_scores or not all(np.isfinite(v) for v in validation_scores.values()):
        raise ValueError("Puntuaciones de validación inválidas.")
    return max(validation_scores, key=validation_scores.get)


def metrics_for(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    per_class = {}
    for i, label in enumerate(CLASSES):
        tp, fn, fp = int(cm[i, i]), int(cm[i].sum() - cm[i, i]), int(cm[:, i].sum() - cm[i, i])
        tn = len(y_true) - tp - fn - fp
        per_class[label] = {"precision": float(precision[i]), "recall": float(recall[i]),
                            "f1": float(f1[i]), "support": int(support[i]), "fp": fp, "fn": fn,
                            "fnr": fn / (tp + fn) if tp + fn else None,
                            "fpr": fp / (tn + fp) if tn + fp else None}
    return {"accuracy": float(accuracy_score(y_true, y_pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "macro_f1": float(f1.mean()), "per_class": per_class,
            "confusion_matrix": cm.tolist(), "class_order": CLASSES,
            "n": len(y_true), "missing_classes": [c for c in CLASSES if c not in set(y_true)]}


def bootstrap_intervals(frame, predictions, samples=500, seed=42):
    # Remuestreo de hilos completos para conservar la dependencia intrahilo.
    rng = np.random.default_rng(seed)
    groups = frame.id_hilo.to_numpy()
    unique = np.unique(groups)
    y, pred = frame.etiqueta.to_numpy(), np.asarray(predictions)
    values = {"macro_f1": [], "precision_odio": [], "recall_odio": [], "fnr_odio": []}
    for _ in range(samples):
        idx = np.concatenate([np.flatnonzero(groups == g) for g in rng.choice(unique, len(unique), replace=True)])
        values["macro_f1"].append(float(f1_score(y[idx], pred[idx], labels=CLASSES, average="macro", zero_division=0)))
        if np.any(y[idx] == "Odio"):
            p, r, _, _ = precision_recall_fscore_support(y[idx], pred[idx], labels=["Odio"], zero_division=0)
            values["precision_odio"].append(float(p[0]))
            values["recall_odio"].append(float(r[0]))
            values["fnr_odio"].append(float(1-r[0]))
    return {key: {"low": float(np.quantile(v, .025)), "high": float(np.quantile(v, .975)), "valid_samples": len(v)} if v else None for key, v in values.items()}


def subgroup_metrics(frame, predictions):
    result = {}
    for column in ["idioma", "subreddit", "tipo_contenido"]:
        result[column] = {}
        for value in frame[column].unique():
            mask = frame[column].to_numpy() == value
            result[column][str(value)] = metrics_for(frame.etiqueta.to_numpy()[mask], np.asarray(predictions)[mask])
    return result
