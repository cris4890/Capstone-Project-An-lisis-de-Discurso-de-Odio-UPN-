"""Validación y minimización de corpus; no realiza extracción de Reddit."""
import argparse
import hashlib
import json
import uuid
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException

from data_pipeline import clean_and_anonymize

CLASSES = ["Odio", "Ofensivo", "Neutro"]
SAFE_COLUMNS = ["id_comentario", "id_hilo", "subreddit", "idioma", "tipo_contenido",
                "fecha", "texto_limpio", "etiqueta", "origen", "idioma_confianza",
                "revision_idioma", "grupo_objetivo", "justificacion"]


def text_identity(text):
    """Clave conservadora contra duplicados; no elimina negaciones ni contexto."""
    return clean_and_anonymize(text).casefold()


def validate_prepared_corpus(frame, require_labels=True):
    """Validación estricta sin eliminar filas ni cambiar IDs de una versión anotada."""
    required = {"id_comentario", "id_hilo", "texto_limpio", "subreddit", "idioma",
                "tipo_contenido", "origen"}
    if require_labels:
        required.add("etiqueta")
    missing = required - set(frame)
    if missing or frame.empty:
        raise ValueError("Corpus vacío o faltan campos requeridos: " + ", ".join(sorted(missing)))
    values = frame[list(required)]
    if values.isna().any().any() or values.astype(str).apply(lambda c: c.str.strip()).eq("").any().any():
        raise ValueError("Hay campos requeridos vacíos.")
    if frame.id_comentario.duplicated().any():
        raise ValueError("Identificadores duplicados.")
    keys = frame.texto_limpio.map(text_identity)
    if keys.eq("").any() or keys.duplicated().any():
        raise ValueError("Textos vacíos o duplicados después de normalización.")
    if frame.origen.nunique() != 1 or not set(frame.origen).issubset({"sintetico", "reddit_autorizado", "licenciado"}):
        raise ValueError("Declare una única procedencia reconocida.")
    for col, permitted in {"subreddit": {"r/Millennials", "r/GenZ"},
                           "idioma": {"es", "en"},
                           "tipo_contenido": {"publicacion", "comentario"}}.items():
        if not set(frame[col]).issubset(permitted):
            raise ValueError(f"Valores inválidos en {col}.")
    if "etiqueta" in frame:
        permitted = CLASSES if require_labels else CLASSES + [""]
        if not frame.etiqueta.fillna("").isin(permitted).all():
            raise ValueError("Etiquetas fuera del esquema Odio/Ofensivo/Neutro.")
    if "revision_idioma" in frame:
        flags = frame.revision_idioma.astype(str).str.strip().str.lower()
        if not flags.isin(["false", "0"]).all():
            raise ValueError("Resuelva la revisión de idioma; indicador inválido o pendiente.")
    return frame


def language_of(text):
    DetectorFactory.seed = 42
    try:
        prediction = detect_langs(text)[0]
        return prediction.lang, float(prediction.prob)
    except LangDetectException:
        return "und", 0.0


def validate_manifest(manifest):
    required = ["fuente", "referencia", "fecha_autorizacion", "alcance", "conservacion_hasta",
                "responsable", "evidencia_archivo", "fecha_inicio", "fecha_fin"]
    missing = [key for key in required if not manifest.get(key) or not str(manifest[key]).strip()]
    if missing or manifest.get("permite_entrenamiento") is not True:
        raise ValueError("Procedencia incompleta o entrenamiento no permitido: " + ", ".join(missing))
    evidence = Path(manifest["evidencia_archivo"])
    if not evidence.is_file():
        raise ValueError("No se encuentra la evidencia de autorización/licencia.")
    dates = pd.to_datetime([manifest[k] for k in ["fecha_autorizacion", "conservacion_hasta", "fecha_inicio", "fecha_fin"]], utc=True, errors="coerce")
    if dates.isna().any() or dates[1] < pd.Timestamp.now(tz="UTC") or dates[2] > dates[3]:
        raise ValueError("Fechas inválidas o plazo de conservación vencido.")
    return hashlib.sha256(evidence.read_bytes()).hexdigest()


def prepare_corpus(df, manifest=None):
    df = df.copy()
    required = {"subreddit", "tipo_contenido", "id_hilo", "origen"}
    if required - set(df.columns):
        raise ValueError("Faltan campos: " + ", ".join(sorted(required - set(df.columns))))
    if df.empty:
        raise ValueError("El corpus está vacío.")
    if df[list(required)].isna().any().any() or (df[list(required)].astype(str).apply(lambda c: c.str.strip()).eq("")).any().any():
        raise ValueError("Los metadatos requeridos no pueden estar vacíos.")
    if not set(df.origen).issubset({"sintetico", "reddit_autorizado", "licenciado"}):
        raise ValueError("Origen no reconocido.")
    if df.origen.nunique() != 1:
        raise ValueError("Mantenga separados los corpus sintéticos y reales.")
    real = df.origen.iloc[0] != "sintetico"
    evidence_hash = validate_manifest(manifest or {}) if real else None
    if not set(df.subreddit).issubset({"r/Millennials", "r/GenZ"}):
        raise ValueError("Comunidad fuera del alcance del PC4; revise la delimitación si usa otro corpus.")
    if not set(df.tipo_contenido).issubset({"publicacion", "comentario"}):
        raise ValueError("Tipo de contenido inválido.")
    original_count = len(df)
    text_col = "texto_original" if "texto_original" in df else "texto_limpio"
    if text_col not in df:
        raise ValueError("Falta el texto del corpus.")
    if "es_bot" in df:
        df = df[~df.es_bot.astype(str).str.lower().isin(["true", "1", "si", "sí"])]
    df = df[~df[text_col].fillna("").astype(str).str.strip().str.lower().isin(["", "[deleted]", "[removed]"])]
    df["texto_limpio"] = df[text_col].apply(clean_and_anonymize)
    analyzable = df.texto_limpio.str.replace(r"\[(?:USER|URL|EMAIL|PHONE)\]", "", regex=True).str.contains(r"[^\W\d_]", regex=True)
    df = df[analyzable].copy()
    df["_text_identity"] = df.texto_limpio.map(text_identity)
    if "etiqueta" in df and df.groupby("_text_identity").etiqueta.nunique().gt(1).any():
        raise ValueError("Textos duplicados con etiquetas contradictorias; requieren revisión.")
    df = df.drop_duplicates("_text_identity").copy()
    if df.empty:
        raise ValueError("No quedaron textos analizables.")
    if real:
        if "fecha" not in df:
            raise ValueError("El corpus real necesita fecha para verificar el periodo.")
        dates = pd.to_datetime(df.fecha, utc=True, errors="coerce")
        if dates.isna().any() or not dates.between(pd.to_datetime(manifest["fecha_inicio"], utc=True), pd.to_datetime(manifest["fecha_fin"], utc=True)).all():
            raise ValueError("Hay fechas inválidas o fuera del periodo autorizado.")
    detected = df.texto_limpio.apply(language_of)
    provided = df.get("idioma", pd.Series("und", index=df.index)).fillna("und")
    df["idioma"] = [lang for lang, score in detected]
    df["idioma_confianza"] = [score for lang, score in detected]
    df["revision_idioma"] = (df.idioma_confianza < .90) | ~df.idioma.isin(["es", "en"]) | (provided.isin(["es", "en"]) & (provided != df.idioma))
    # Las etiquetas de idioma del generador son conocidas, no inferidas de usuarios.
    if not real:
        df["idioma"] = provided
        df["revision_idioma"] = ~provided.isin(["es", "en"])
    thread_map = {value: str(uuid.uuid4() if real else uuid.uuid5(uuid.NAMESPACE_URL, "hatedetect:synthetic:thread:" + str(value))) for value in df.id_hilo.unique()}
    df["id_hilo"] = df.id_hilo.map(thread_map)
    df["id_comentario"] = [str(uuid.uuid4() if real else uuid.uuid5(uuid.NAMESPACE_URL, "hatedetect:synthetic:text:" + key)) for key in df._text_identity]
    if "etiqueta" not in df:
        df["etiqueta"] = ""
    if not df.etiqueta.fillna("").isin(CLASSES + [""]).all():
        raise ValueError("Etiquetas fuera del esquema Odio/Ofensivo/Neutro.")
    for col in ["grupo_objetivo", "justificacion"]:
        if col in df:
            df[col] = df[col].apply(clean_and_anonymize)
    result = df[[col for col in SAFE_COLUMNS if col in df]].reset_index(drop=True)
    report = {"input_rows": original_count, "output_rows": len(result),
              "removed_rows": original_count - len(result), "language_review": int(result.revision_idioma.sum()),
              "origin": result.origen.iloc[0], "authorization_evidence_sha256": evidence_hash,
              "privacy_limit": "Enmascaramiento automático; requiere revisión humana de nombres y contexto identificable."}
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--manifest")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8")) if args.manifest else None
    df, report = prepare_corpus(pd.read_csv(args.input), manifest)
    output = Path(args.output)
    if output.exists() or output.with_suffix(".quality.json").exists():
        raise FileExistsError("Use una ruta nueva para conservar la versión anterior.")
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    report["corpus_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".quality.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
