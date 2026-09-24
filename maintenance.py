"""Respaldo y restauración verificables de SQLite, sin sobrescribir bases existentes."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile


def backup_database(source, archive):
    source, archive = Path(source).resolve(), Path(archive).resolve()
    if not source.is_file():
        raise FileNotFoundError("No existe la base de datos indicada.")
    if archive.exists():
        raise FileExistsError("El respaldo ya existe; use una ruta nueva.")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        snapshot = Path(temporary)/"database.sqlite3"
        # La API de backup incorpora transacciones confirmadas, incluso con WAL.
        with closing(sqlite3.connect(source.as_uri()+"?mode=ro", uri=True)) as origin:
            with closing(sqlite3.connect(snapshot)) as destination:
                origin.backup(destination)
                if destination.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("La base no superó la comprobación de integridad.")
        data = snapshot.read_bytes()
        manifest = {"schema":1, "created_at":datetime.now(timezone.utc).isoformat(),
                    "sha256":hashlib.sha256(data).hexdigest(), "bytes":len(data),
                    "encrypted":False}
        with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED) as output:
            output.writestr("database.sqlite3",data)
            output.writestr("manifest.json",json.dumps(manifest,indent=2))
    return manifest


def restore_database(archive, destination):
    archive, destination = Path(archive).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError("La restauración requiere una ruta nueva; no se sobrescribe la base actual.")
    with zipfile.ZipFile(archive) as source:
        if sorted(source.namelist()) != ["database.sqlite3", "manifest.json"]:
            raise ValueError("El archivo no es un respaldo compatible.")
        # Nunca extraer rutas aportadas por el archivo ZIP.
        manifest = json.loads(source.read("manifest.json"))
        data = source.read("database.sqlite3")
    if manifest.get("schema") != 1 or manifest.get("sha256") != hashlib.sha256(data).hexdigest() or manifest.get("bytes") != len(data):
        raise ValueError("El respaldo no supera la comprobación de integridad.")
    with tempfile.TemporaryDirectory() as temporary:
        sample = Path(temporary)/"database.sqlite3"
        sample.write_bytes(data)
        with closing(sqlite3.connect(sample.as_uri()+"?mode=ro", uri=True)) as conn:
            if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("El contenido restaurado no es íntegro.")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("xb") as output:
        output.write(data)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command",required=True)
    backup = commands.add_parser("backup")
    backup.add_argument("--database",required=True)
    backup.add_argument("--output",required=True)
    restore = commands.add_parser("restore")
    restore.add_argument("--archive",required=True)
    restore.add_argument("--database",required=True)
    args = parser.parse_args()
    result = backup_database(args.database,args.output) if args.command == "backup" else restore_database(args.archive,args.database)
    print(json.dumps(result,ensure_ascii=False,indent=2))
