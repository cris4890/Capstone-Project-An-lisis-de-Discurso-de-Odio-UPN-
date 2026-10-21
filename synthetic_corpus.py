"""Exportación auditable de los 72 ejemplos existentes; no inventa revisión humana."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from corpus import prepare_corpus, text_identity, validate_prepared_corpus
from data_pipeline import generate_synthetic_data

ROOT = Path(__file__).resolve().parent
KPI_PATH = ROOT / "docs/sprint2/evidencias/casos_30.json"


def reject_kpi_overlap(frame):
    """El piloto histórico queda excluido de cualquier partición de desarrollo."""
    cases = json.loads(KPI_PATH.read_text(encoding="utf-8"))
    reserved = {text_identity(case["texto"]): case["id"] for case in cases}
    overlap = sorted({reserved[key] for key in frame.texto_limpio.map(text_identity) if key in reserved})
    if overlap:
        raise ValueError("El corpus contiene casos reservados del piloto KPI: " + ", ".join(overlap))
    return {"reserved_cases": len(cases), "normalized_exact_overlap": 0,
            "pilot_sha256": hashlib.sha256(KPI_PATH.read_bytes()).hexdigest(),
            "limit": "No detecta paráfrasis ni acredita independencia científica de ejemplos conocidos."}


def export_for_review(output):
    out = Path(output)
    if out.exists():
        raise FileExistsError("Use una carpeta nueva; no se sobrescribe una revisión anterior.")
    frame, quality = prepare_corpus(generate_synthetic_data())
    validate_prepared_corpus(frame)
    isolation = reject_kpi_overlap(frame)
    blinded = frame.copy()
    blinded["etiqueta"] = ""
    proposals = frame[["id_comentario", "etiqueta"]].rename(columns={"etiqueta": "etiqueta_propuesta"})
    template = frame[["id_comentario", "texto_limpio", "idioma"]].copy()
    for column in ["etiqueta", "grupo_objetivo", "justificacion", "evaluador", "fecha_revision", "observaciones"]:
        template[column] = ""
    template["estado_revision"] = "pendiente"
    out.mkdir(parents=True)
    for name, data in [("corpus_para_anotar.csv", blinded), ("propuestas_generador.csv", proposals),
                       ("corpus_exploratorio.csv", frame), ("plantilla_revision.csv", template)]:
        data.to_csv(out / name, index=False, encoding="utf-8", lineterminator="\n")
    manifest = {"schema_version": 1, "exported_at_utc": datetime.now(timezone.utc).isoformat(),
                "origin": "sintetico", "source": "data_pipeline.generate_synthetic_data",
                "generator_sha256": hashlib.sha256((ROOT / "data_pipeline.py").read_bytes()).hexdigest(),
                "rows": len(frame), "review_status": "pendiente", "reviewers": [],
                "authors_confirmed": [], "human_approval_date": None,
                "scope": "T2 del curso; autorización docente comunicada por el solicitante, no acta verificada",
                "quality": quality, "kpi_isolation": isolation,
                "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("*.csv")}}
    (out / "procedencia.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    export = actions.add_parser("exportar")
    export.add_argument("--output", required=True)
    validate = actions.add_parser("validar")
    validate.add_argument("input")
    validate.add_argument("--sin-etiquetas", action="store_true")
    args = parser.parse_args()
    if args.action == "exportar":
        report = export_for_review(args.output)
    else:
        frame = pd.read_csv(args.input, dtype={"id_comentario": str, "id_hilo": str})
        validate_prepared_corpus(frame, require_labels=not args.sin_etiquetas)
        if set(frame.origen) != {"sintetico"}:
            raise ValueError("Este procedimiento T2 admite únicamente corpus sintético.")
        report = {"rows": len(frame), "structural_validation": "passed",
                  "human_review": "no acreditada por esta validación", "kpi_isolation": reject_kpi_overlap(frame)}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
