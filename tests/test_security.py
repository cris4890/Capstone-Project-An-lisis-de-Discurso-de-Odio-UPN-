from contextlib import closing
import json
import sqlite3
from pathlib import Path
import zipfile
import pytest
from maintenance import backup_database, restore_database


def test_backup_restore_preserves_records_and_does_not_overwrite(tmp_path):
    source, archive, restored = [tmp_path/name for name in ["source.sqlite3","backup.zip","restored.sqlite3"]]
    with closing(sqlite3.connect(source)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE evidence(value TEXT)")
        conn.execute("INSERT INTO evidence VALUES (?)",("synthetic-test",))
        conn.commit()
        meta = backup_database(source,archive)
    assert len(meta["sha256"]) == 64
    restore_database(archive,restored)
    with closing(sqlite3.connect(restored)) as conn:
        assert conn.execute("SELECT value FROM evidence").fetchone()[0] == "synthetic-test"
    with pytest.raises(FileExistsError):
        restore_database(archive,restored)
    with pytest.raises(FileExistsError):
        backup_database(source,archive)


def test_corrupt_archive_rejected_without_destination(tmp_path):
    archive, destination = tmp_path/"bad.zip",tmp_path/"new.sqlite3"
    with zipfile.ZipFile(archive,"w") as output:
        output.writestr("database.sqlite3",b"altered")
        output.writestr("manifest.json",json.dumps({"schema":1,"sha256":"bad","bytes":7}))
    with pytest.raises(ValueError,match="integridad"):
        restore_database(archive,destination)
    assert not destination.exists()


def test_local_server_defaults():
    import tomllib
    config = tomllib.loads((Path(__file__).parents[1]/".streamlit/config.toml").read_text(encoding="utf-8"))
    assert config["server"]["address"] == "127.0.0.1"
    assert config["server"]["enableXsrfProtection"] and config["server"]["enableCORS"]
