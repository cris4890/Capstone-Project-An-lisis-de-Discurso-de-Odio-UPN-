"""Ejecuta éxito, mutación controlada y restauración en una copia aislada."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "entregables/laboratorio_unitarias/evidencias")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources = ["data_pipeline.py", "experiment.py", "tests/test_laboratorio_unitarias.py"]
    initial = {p: digest(ROOT / p) for p in sources}
    summary = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
               "fuentes_sha256": initial, "ejecuciones": []}
    original = (ROOT / "experiment.py").read_text(encoding="utf-8")
    before = "return max(validation_scores, key=validation_scores.get)"
    after = "return min(validation_scores, key=validation_scores.get)"
    if original.count(before) != 1:
        raise RuntimeError("La función cambió; revise la mutación antes de ejecutarla.")
    (out / "mutacion.txt").write_text("Solo en copia temporal de experiment.py\n- " + before + "\n+ " + after + "\n", encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="hatedetect_lab_") as directory:
        copy = Path(directory)
        for name in sources:
            target = copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        for phase in ["01_correcto", "02_fallo_controlado", "03_restaurado"]:
            (copy / "experiment.py").write_text(original.replace(before, after) if phase == "02_fallo_controlado" else original, encoding="utf-8")
            xml = out / (phase + ".xml")
            command = [sys.executable, "-B", "-m", "pytest", "tests/test_laboratorio_unitarias.py", "-v", "-o", "junit_family=xunit1", "--junitxml=" + str(xml)]
            result = subprocess.run(command, cwd=copy, env=env, capture_output=True, text=True, encoding="utf-8")
            (out / (phase + ".txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
            if not xml.exists():
                raise RuntimeError(result.stdout + result.stderr)
            tree = ET.parse(xml)
            cases = []
            for case in tree.findall(".//testcase"):
                props = {p.attrib["name"]: p.attrib["value"] for p in case.findall("./properties/property")}
                cases.append(dict(props, nombre=case.attrib["name"], segundos=case.attrib["time"], estado="FALLÓ" if case.find("failure") is not None else "ERROR" if case.find("error") is not None else "OMITIDO" if case.find("skipped") is not None else "PASÓ"))
            entry = {"fase": phase, "codigo_salida": result.returncode, "casos": cases}
            summary["ejecuciones"].append(entry)
            print(phase, "exit=", result.returncode, "casos=", len(cases), flush=True)
    summary["fuentes_intactas"] = all(digest(ROOT / p) == h for p, h in initial.items())
    (out / "resumen.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    with (out / "matriz_final.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        fields = ["caso", "entrada", "esperado", "observado", "estado", "segundos"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summary["ejecuciones"][-1]["casos"])
    expected = [["PASÓ"] * 10, ["PASÓ"] * 5 + ["FALLÓ"] + ["PASÓ"] * 4, ["PASÓ"] * 10]
    for entry, statuses, code in zip(summary["ejecuciones"], expected, [0, 1, 0]):
        if entry["codigo_salida"] != code or [c["estado"] for c in entry["casos"]] != statuses:
            raise RuntimeError("Resultado distinto al previsto. Revise " + entry["fase"])
    if not summary["fuentes_intactas"]:
        raise RuntimeError("Las fuentes originales cambiaron durante la ejecución.")


if __name__ == "__main__":
    main()
