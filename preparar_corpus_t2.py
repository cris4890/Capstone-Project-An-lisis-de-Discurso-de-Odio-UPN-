#!/usr/bin/env python3
"""T2 HateDetect: hoja de revisión, validación y corpus preparado.
Ejecutar en la raíz del repositorio HateDetect, con requirements.lock.txt instalado.
No etiqueta ni autentica revisiones por su cuenta, ni descarga datos de Reddit.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

LABELS = {"Odio", "Ofensivo", "Neutro"}
SCENARIOS = {"r/Millennials", "r/GenZ"}
LANGS = {"es", "en"}
COLS = ["id_comentario", "subreddit", "idioma", "texto_original", "etiqueta_original",
        "etiqueta_validada", "autor_creacion", "fecha_creacion", "revisor_etiqueta",
        "fecha_revision", "decision", "justificacion_revision", "id_hilo",
        "tipo_contenido", "origen"]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records, columns):
    if path.exists():
        raise FileExistsError(f"Se conserva el archivo existente: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exportar(path: Path):
    from data_pipeline import generate_synthetic_data
    frame = generate_synthetic_data()
    rows = []
    for item in frame.to_dict("records"):
        rows.append({
            "id_comentario": item["id_comentario"],
            "subreddit": item["subreddit"],
            "idioma": item["idioma"],
            "texto_original": item["texto_original"],
            "etiqueta_original": item["etiqueta"],
            "etiqueta_validada": "",  # NO supone que el equipo la revisó
            "autor_creacion": "", "fecha_creacion": "", "revisor_etiqueta": "",
            "fecha_revision": "", "decision": "pendiente",
            "justificacion_revision": "",
            "id_hilo": item["id_hilo"], "tipo_contenido": item["tipo_contenido"],
            "origen": "sintetico",
        })
    write_csv(path, rows, COLS)
    print(json.dumps({"estado": "hoja_de_revision_generada", "registros": len(rows),
                      "etiquetas_propuestas": dict(Counter(r["etiqueta_original"] for r in rows)),
                      "archivo": str(path), "sha256": sha256(path),
                      "advertencia": "Autoría y revisión PENDIENTES; NO es corpus validado"},
                     ensure_ascii=False, indent=2))


def validar(entrada: Path, salida: Path):
    entrada, salida = Path(entrada), Path(salida)
    report = entrada.with_name(entrada.stem+"_auditoria.json")
    manifest_path = salida.with_suffix(".manifest.json")
    targets = [report, salida, manifest_path]
    if len({p.resolve() for p in [entrada, *targets]}) != 4:
        raise ValueError("Entrada, corpus, auditoría y manifiesto deben ser rutas distintas.")
    for path in targets:
        if path.exists():
            raise FileExistsError(f"Se conserva el archivo existente: {path}")
    rows = read_csv(entrada)
    if not rows:
        raise ValueError("El archivo de revisión está vacío.")
    if not set(COLS).issubset(rows[0]):
        raise ValueError("Faltan columnas: " + ", ".join(sorted(set(COLS)-set(rows[0]))))
    from data_pipeline import clean_and_anonymize
    seen_ids, seen_clean = set(), set()
    problems, accepted = [], []
    for n, item in enumerate(rows, start=2):
        p=[]
        get=lambda k: (item.get(k) or "").strip()
        uid=get("id_comentario")
        raw=get("texto_original")
        lbl=get("etiqueta_validada")
        author=get("autor_creacion")
        reviewer=get("revisor_etiqueta")
        if not uid or uid in seen_ids: p.append("ID ausente o repetido")
        seen_ids.add(uid)
        clean=clean_and_anonymize(raw) if raw else ""
        if not clean or clean.casefold() in seen_clean: p.append("texto vacío o duplicado tras limpieza")
        if clean: seen_clean.add(clean.casefold())
        if lbl not in LABELS: p.append("etiqueta_validada inválida o ausente")
        if get("etiqueta_original") not in LABELS: p.append("etiqueta_original inválida")
        if get("idioma") not in LANGS: p.append("idioma inválido")
        if get("subreddit") not in SCENARIOS: p.append("escenario inválido")
        if get("origen") != "sintetico": p.append("origen distinto de sintetico")
        if get("tipo_contenido") != "comentario": p.append("tipo de contenido no es comentario")
        if not get("id_hilo"): p.append("id_hilo requerido")
        if not author or not get("fecha_creacion"): p.append("autor y fecha de creación pendientes")
        if not reviewer or not get("fecha_revision"): p.append("revisor y fecha de revisión pendientes")
        try:
            created = datetime.strptime(get("fecha_creacion"), "%Y-%m-%d").date()
            reviewed = datetime.strptime(get("fecha_revision"), "%Y-%m-%d").date()
            if created > reviewed or reviewed > datetime.now(timezone.utc).date():
                p.append("fechas fuera de orden o futuras")
        except ValueError:
            p.append("fechas requeridas en formato YYYY-MM-DD válido")
        if author and reviewer and author.casefold()==reviewer.casefold(): p.append("la revisión independiente requiere otra persona")
        if get("decision").casefold() != "aprobado": p.append("decisión aún no aprobada")
        if not get("justificacion_revision"): p.append("falta justificación de etiqueta")
        if p: problems.append({"fila_csv":n,"id":uid,"problemas":p})
        else: accepted.append({"id_comentario":uid,"id_hilo":get("id_hilo"),
                               "subreddit":get("subreddit"), "idioma":get("idioma"),
                               "tipo_contenido":"comentario", "texto_original":raw,
                               "etiqueta":lbl,"origen":"sintetico"})
    dist=Counter(z["etiqueta"] for z in accepted)
    if len(accepted)<18 or any(dist.get(label,0)<5 for label in LABELS):
        problems.append({"global":"Para la partición demostrativa se requieren al menos 18 ejemplos validados y 5 por clase (mínimo técnico, no tamaño científico)."})
    if not problems:
        import pandas as pd
        from corpus import prepare_corpus, SAFE_COLUMNS, validate_prepared_corpus
        from synthetic_corpus import reject_kpi_overlap
        from experiment import split_corpus
        try:
            frame, report_corpus = prepare_corpus(pd.DataFrame(accepted))
            if len(frame) != len(accepted):
                raise ValueError("El preprocesamiento eliminó filas.")
            validate_prepared_corpus(frame)
            reject_kpi_overlap(frame)
            split_corpus(frame, 42)
        except ValueError as exc:
            problems.append({"global": str(exc)})
    summary={"fecha_utc": datetime.now(timezone.utc).isoformat(),
             "entrada":str(entrada),"sha256_entrada":sha256(entrada),
             "total":len(rows),"aprobados_registro":len(accepted),
             "etiquetas_aprobadas":dict(dist),"incidencias":problems,
             "resultado":"APTO_PARA_PREPARAR" if not problems else "NO_APTO_PARA_ENTRENAR",
             "nota":"No acredita aprobación docente ni independencia real; depende de la revisión documentada."}
    report = entrada.with_name(entrada.stem+"_auditoria.json")
    if report.exists():
        raise FileExistsError(f"No sobrescribir auditoría existente: {report}")
    report.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    if problems:
        print(json.dumps({k:v for k,v in summary.items() if k!="incidencias"},ensure_ascii=False,indent=2))
        print(f"Incidencias: {len(problems)}. Primeras 15: "+json.dumps(problems[:15],ensure_ascii=False))
        raise SystemExit(2)
    # La hoja no sustituye las dos anotaciones y adjudicación exigidas por HU-03.
    write_csv(salida,frame.to_dict("records"),[c for c in SAFE_COLUMNS if c in frame.columns])
    manifest={"alcance":"T2 corpus sintético con revisión declarada; no procede de Reddit",
              "estado":"revision_declarada_no_autenticada; anotacion_HU03_requerida",
              "evidencia_revision":str(entrada), "sha256_revision":sha256(entrada),
              "archivo_corpus":str(salida),"sha256_corpus":sha256(salida),
              "n":len(frame),"clases":dict(Counter(frame.etiqueta)),
              "reporte_preprocesamiento":report_corpus,
              "limitaciones":["La autoría y revisión declaradas en la hoja requieren verificación humana",
                              "Las comunidades r/Millennials y r/GenZ son escenarios simulados",
                              "No acredita representatividad ni permiso Reddit"]}
    manifest_path=salida.with_suffix(".manifest.json")
    if manifest_path.exists(): raise FileExistsError(f"Manifiesto existente: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"estado":"corpus_preparado","archivo":str(salida),
                      "manifiesto":str(manifest_path),"n":len(frame),
                      "distribucion":manifest["clases"]},ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="accion",required=True)
    p=sub.add_parser("exportar",help="Exporta los 72 ejemplos existentes para revisión humana")
    p.add_argument("--salida",default="private/t2_revision_pendiente.csv",type=Path)
    p=sub.add_parser("validar",help="Valida que la revisión humana esté documentada")
    p.add_argument("--entrada",required=True,type=Path)
    p.add_argument("--salida",default="private/t2_corpus_validado.csv",type=Path)
    args=parser.parse_args()
    if args.accion=="exportar": exportar(args.salida)
    else: validar(args.entrada,args.salida)

if __name__=="__main__": main()
