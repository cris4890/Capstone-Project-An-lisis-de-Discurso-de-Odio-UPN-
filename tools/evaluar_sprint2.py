"""Reproduce el piloto y genera evidencias sin sustituir tiempos faltantes."""
import csv
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from context_rules import ContextRuleBasedClassifier
from data_pipeline import clean_and_anonymize
from experiment import metrics_for

OUT = ROOT / "docs/sprint2/evidencias"


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    cases = json.loads((OUT / "casos_30.json").read_text(encoding="utf-8"))
    historical = json.loads((OUT / "piloto_historico.json").read_text(encoding="utf-8"))
    model = ContextRuleBasedClassifier()
    results = []
    browser = json.loads((OUT / "e2e_navegador.json").read_text(encoding="utf-8")) if (OUT / "e2e_navegador.json").exists() else []
    by_id = {row["id"]: row for row in browser}
    for case in cases:
        cleaned = clean_and_anonymize(case["texto"])
        start = time.perf_counter()
        prediction = model.predict([cleaned])[0]
        elapsed = time.perf_counter() - start
        observation = by_id.get(case["id"], {})
        results.append(dict(case, hatedetect=prediction, inferencia_segundos=elapsed,
                            e2e_segundos=observation.get("seconds"),
                            navegador_categoria=observation.get("prediction"),
                            coincide_referencia=prediction == case["referencia"]))
    reference = [c["referencia"] for c in cases]
    current = metrics_for(reference, [r["hatedetect"] for r in results])
    old = metrics_for(reference, [r["categoria"] for r in historical["resultados"]])
    dump("piloto_actual.json", results)
    dump("metricas.json", {"actual": current, "historico": old,
         "referencia": "Clave de la ficha del usuario; textos sintéticos, independencia no acreditada",
         "comparacion_manual": "Datos manuales aportados; límites temporales no equivalentes, comparación descriptiva",
         "e2e_n": len(browser), "n": len(cases)})
    for name, rows in [("anexo_kpi.csv", results), ("errores.csv", [r for r in results if not r["coincide_referencia"]])]:
        with (OUT / name).open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(rows)
    labels = current["class_order"]
    with (OUT / "matriz_confusion.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Referencia / Predicción"] + labels)
        writer.writerows([[label] + row for label, row in zip(labels, current["confusion_matrix"])])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4.6))
    ax.imshow(current["confusion_matrix"], cmap="Blues", vmin=0)
    ax.set(xticks=range(3), yticks=range(3), xticklabels=labels, yticklabels=labels,
           xlabel="Predicción HateDetect", ylabel="Referencia de trabajo",
           title="Piloto sintético de 30 casos · Reglas v2")
    for i, row in enumerate(current["confusion_matrix"]):
        for j, value in enumerate(row):
            ax.text(j, i, str(value), ha="center", va="center", color="white" if value > 5 else "black", fontsize=18)
    fig.tight_layout()
    fig.savefig(OUT / "matriz_confusion.png", dpi=170)
    plt.close(fig)
    tests = []
    if (OUT / "pruebas.xml").exists():
        for case in ET.parse(OUT / "pruebas.xml").findall(".//testcase"):
            props = {p.get("name"): p.get("value") for p in case.findall("./properties/property")}
            status = "fallo" if case.find("failure") is not None else "error" if case.find("error") is not None else "omitida" if case.find("skipped") is not None else "aprobada"
            tests.append({"prueba": case.get("classname") + "::" + case.get("name"), "tipo": props.get("tipo_prueba", "sin clasificar"), "resultado": status, "segundos": case.get("time")})
        with (OUT / "inventario_pruebas.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=["prueba", "tipo", "resultado", "segundos"])
            writer.writeheader()
            writer.writerows(tests)
    sources = ["app.py", "context_rules.py", "data_pipeline.py", "e2e_probe.py", "e2e_probe.html", "tests/conftest.py"]
    dump("version.json", {"fecha_utc": datetime.now(timezone.utc).isoformat(),
         "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "nota": "El commit base puede preceder al commit de evidencias; estos hashes identifican las fuentes probadas.",
         "modelo": "ContextRuleBasedClassifier 2.0",
         "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
         "casos_sha256": hashlib.sha256((OUT / "casos_30.json").read_bytes()).hexdigest()})
    lines = ["# Resultados verificados de Sprint 2", "", f"Piloto: {sum(r['coincide_referencia'] for r in results)}/30 aciertos; exactitud {current['accuracy']:.0%}.",
             "", "Referencia de trabajo sintética; no es evaluación científica final.", "", "| Clase | Soporte | FP | FN | Recall |", "| --- | ---: | ---: | ---: | ---: |"]
    for label, m in current["per_class"].items():
        lines.append(f"| {label} | {m['support']} | {m['fp']} | {m['fn']} | {m['recall']:.1%} |")
    lines += ["", f"Tiempos E2E registrados en navegador: {len(browser)}/30.",
              "Los tiempos de inferencia no se usan como tiempo total ni se comparan directamente con el proceso manual.",
              "Clasificación manual y tiempos: ficha aportada del 04/10/2026. No se acredita cegamiento ni equivalencia del intervalo cronometrado.",
              "Cobertura de respuesta = casos con resultado / casos enviados; no equivale a recall ni exactitud.", "",
              f"Suite: {len(tests)} casos; aprobados: {sum(t['resultado']=='aprobada' for t in tests)}.",
              "", "| Tipo | Casos |", "| --- | ---: |"]
    for kind in ["unitaria", "integracion", "sistema", "aceptacion"]:
        lines.append(f"| {kind} | {sum(t['tipo']==kind for t in tests)} |")
    lines += ["", "Aceptación formal: pendiente de Review humana; no se deduce de pytest."]
    if browser:
        times = [float(r["seconds"]) for r in browser]
        lines += ["", f"Tiempo E2E medio observado: {sum(times)/len(times):.3f} s. Total de ventanas medidas: {sum(times):.3f} s.",
                  "Medición clic a marcador de resultado y dos frames. Excluye lectura, preparación del texto y revisión humana; no equivale al tiempo total del trabajo manual."]
    manual_times = [c["manual_segundos"] for c in cases]
    if all(isinstance(t, (int, float)) and t > 0 for t in manual_times):
        manual_total = sum(manual_times)
        manual_correct = sum(c["manual_categoria"] == c["referencia"] for c in cases)
        accumulated = 0
        covered = 0
        for t in manual_times:
            accumulated += t
            covered += accumulated <= 60
        kpi = {"manual": {"total_segundos": manual_total, "media_segundos": manual_total/len(cases),
              "aciertos": manual_correct, "exactitud": manual_correct/len(cases), "errores": len(cases)-manual_correct,
              "textos_por_minuto": len(cases)*60/manual_total, "cobertura_60s": covered/len(cases)},
              "hatedetect": {"exactitud": current["accuracy"], "aciertos": sum(r['coincide_referencia'] for r in results)},
              "comparacion_causal_valida": False,
              "limitacion": "El E2E excluye ingreso y revisión humana; no equivale al protocolo manual. No afirmar ahorro laboral ni productividad integral."}
        if browser:
            kpi["hatedetect"].update(total_ventanas_segundos=sum(times), media_e2e_segundos=sum(times)/len(times),
                capacidad_ventanas_textos_minuto=len(times)*60/sum(times),
                cobertura_ventanas_60s=sum(sum(times[:i+1])<=60 for i in range(len(times)))/len(cases))
        dump("kpi.json", kpi)
        lines += ["", f"Manual: {manual_total:.2f} s, media {manual_total/len(cases):.3f} s, {manual_correct}/30 aciertos, {covered}/30 antes de 60 s acumulados.",
                  "La capacidad calculada sobre ventanas E2E es descriptiva; excluye intervalos entre casos, ingreso y revisión. No se presenta como mejora causal de productividad."]
    (ROOT / "docs/sprint2/RESULTADOS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
