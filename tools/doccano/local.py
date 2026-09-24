"""Doccano pilot isolated from the classifier; bind only to localhost."""
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "private" / "doccano" / "data"
DATA.mkdir(parents=True, exist_ok=True)
key = DATA / "secret.txt"
if not key.exists():
    key.write_text(secrets.token_urlsafe(48), encoding="utf-8")
os.environ["DOCCANO_HOME"] = str(DATA)
os.environ["SECRET_KEY"] = key.read_text(encoding="utf-8")
os.environ["ALLOWED_HOSTS"] = "127.0.0.1,localhost,testserver"
os.environ["CELERY_BROKER_URL"] = "sqla+sqlite:///" + (DATA / "queue.sqlite3").as_posix()
os.chdir(DATA)
import backend.cli as cli

def local_server(args):
    from waitress import serve
    from config.wsgi import application
    serve(application, host="127.0.0.1", port=args.port, threads=4)

cli.run_on_windows = local_server
if __name__ == "__main__":
    cli.main()
