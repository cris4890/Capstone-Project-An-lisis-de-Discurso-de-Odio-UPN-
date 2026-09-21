"""Carga únicamente artefactos de ejecuciones locales completas."""
import json
from pathlib import Path
import joblib
from model_classes import RuleBasedClassifier, TransformerClassifier


def load_run_model(run_dir, key):
    run_dir = Path(run_dir)
    manifest_path = run_dir / "run.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("Seleccione una ejecución completa antes de cargar un modelo.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if key == "selected":
        key = manifest["selected_model"]
    if key not in manifest["models"]:
        raise FileNotFoundError("Este modelo no fue entrenado en la ejecución seleccionada.")
    entry = manifest["models"][key]
    artifact = (run_dir / entry["artifact"]).resolve()
    if not artifact.is_relative_to(run_dir.resolve()):
        raise ValueError("Ruta de artefacto fuera de la ejecución.")
    if entry["kind"] == "transformer":
        model = TransformerClassifier.load(artifact)
    else:
        if not artifact.is_file():
            raise FileNotFoundError("Falta el archivo del modelo; no se sustituye por otro.")
        model = joblib.load(artifact)
    return model, entry["name"]
