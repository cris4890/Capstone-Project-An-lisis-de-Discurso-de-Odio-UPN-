"""Package integration; declared reviewers below are isolated test fixtures only."""
import json
import pytest
import preparar_corpus_t2 as package

pytestmark = pytest.mark.integracion


def revision(tmp_path):
    draft = tmp_path / "draft.csv"
    package.exportar(draft)
    rows = package.read_csv(draft)
    for row in rows:
        row.update(etiqueta_validada=row["etiqueta_original"],
                   autor_creacion="FIXTURE_AUTHOR", revisor_etiqueta="FIXTURE_REVIEWER",
                   fecha_creacion="2020-01-01", fecha_revision="2020-01-02",
                   decision="aprobado", justificacion_revision="Simulación exclusiva del test")
    return rows


def test_package_exports_pending_and_blocks_training(tmp_path):
    path = tmp_path / "pending.csv"
    package.exportar(path)
    rows = package.read_csv(path)
    assert len(rows) == 72
    assert all(r["decision"] == "pendiente" and not r["autor_creacion"] for r in rows)
    with pytest.raises(SystemExit) as exc:
        package.validar(path, tmp_path / "out.csv")
    assert exc.value.code == 2
    assert not (tmp_path / "out.csv").exists()


@pytest.mark.parametrize("field,value", [
    ("fecha_revision", "ayer"), ("fecha_revision", "2019-01-01"),
    ("fecha_revision", "2999-01-01"), ("revisor_etiqueta", "FIXTURE_AUTHOR"),
    ("etiqueta_validada", "Neutral"), ("idioma", "fr"), ("origen", "reddit"),
])
def test_package_rejects_invalid_review(tmp_path, field, value):
    rows = revision(tmp_path)
    rows[0][field] = value
    path = tmp_path / "review.csv"
    package.write_csv(path, rows, package.COLS)
    with pytest.raises(SystemExit):
        package.validar(path, tmp_path / "out.csv")
    assert not (tmp_path / "out.csv").exists()


def test_package_kpi_rejected_before_approval(tmp_path):
    from synthetic_corpus import KPI_PATH
    rows = revision(tmp_path)
    rows[0]["texto_original"] = json.loads(KPI_PATH.read_text(encoding="utf-8"))[0]["texto"]
    path = tmp_path / "review.csv"
    package.write_csv(path, rows, package.COLS)
    with pytest.raises(SystemExit):
        package.validar(path, tmp_path / "out.csv")
    report = json.loads((tmp_path / "review_auditoria.json").read_text(encoding="utf-8"))
    assert report["resultado"] == "NO_APTO_PARA_ENTRENAR"


def test_package_prepares_compatible_corpus_without_authenticating_people(tmp_path):
    import pandas as pd
    from corpus import validate_prepared_corpus
    from train_models import run_training_pipeline
    rows = revision(tmp_path)
    path, out = tmp_path / "review.csv", tmp_path / "out.csv"
    package.write_csv(path, rows, package.COLS)
    package.validar(path, out)
    frame = pd.read_csv(out)
    validate_prepared_corpus(frame)
    assert len(frame) == 72
    assert "autor_creacion" not in frame.columns
    with pytest.raises(ValueError, match="base existente"):
        run_training_pipeline(out, tmp_path / "run", synthetic_mode="reviewed")
    manifest = json.loads(out.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert manifest["sha256_corpus"] == package.sha256(out)
    assert "no_autenticada" in manifest["estado"]


def test_package_preserves_existing_manifest_before_any_write(tmp_path):
    rows = revision(tmp_path)
    path, out = tmp_path / "review.csv", tmp_path / "out.csv"
    package.write_csv(path, rows, package.COLS)
    out.with_suffix(".manifest.json").write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        package.validar(path, out)
    assert not out.exists()
    assert not (tmp_path / "review_auditoria.json").exists()
