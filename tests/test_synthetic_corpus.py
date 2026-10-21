import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from corpus import prepare_corpus, validate_prepared_corpus
from data_pipeline import generate_synthetic_data, process_and_save
from experiment import split_corpus
from synthetic_corpus import export_for_review, reject_kpi_overlap, KPI_PATH


@pytest.fixture(scope="module")
def prepared():
    return prepare_corpus(generate_synthetic_data())[0]


def test_synthetic_ids_and_partitions_repeat_across_preparations(prepared):
    other = prepare_corpus(generate_synthetic_data())[0]
    pd.testing.assert_frame_equal(prepared, other)
    a, b = split_corpus(prepared), split_corpus(other)
    for partition in a:
        assert a[partition].id_comentario.tolist() == b[partition].id_comentario.tolist()


@pytest.mark.parametrize("column,value", [
    ("etiqueta", "Neutral"), ("etiqueta", ""), ("idioma", "fr"),
    ("origen", "desconocido"), ("subreddit", "r/otro"),
    ("tipo_contenido", "usuario"), ("id_hilo", " "), ("texto_limpio", None),
    ("revision_idioma", True), ("revision_idioma", "pendiente"),
])
def test_invalid_prepared_fields_are_rejected(prepared, column, value):
    frame = prepared.copy().astype({column: object})
    frame.loc[0, column] = value
    with pytest.raises(ValueError):
        validate_prepared_corpus(frame)


@pytest.mark.parametrize("column", ["origen", "id_hilo", "texto_limpio", "etiqueta", "idioma"])
def test_missing_columns_are_rejected(prepared, column):
    with pytest.raises(ValueError, match="campos"):
        validate_prepared_corpus(prepared.drop(columns=[column]))


def test_normalized_duplicates_and_conflicting_labels_rejected(prepared):
    frame = prepared.copy()
    frame.loc[1, "texto_limpio"] = "  " + frame.loc[0, "texto_limpio"].upper() + "  "
    with pytest.raises(ValueError, match="duplicados"):
        validate_prepared_corpus(frame)
    with pytest.raises(ValueError, match="duplicados"):
        split_corpus(frame)
    frame.loc[1, "etiqueta"] = "Neutro"
    with pytest.raises(ValueError, match="contradictorias"):
        prepare_corpus(frame)


def test_mixed_origins_and_duplicate_ids_rejected(prepared):
    frame = prepared.copy()
    frame.loc[0, "origen"] = "reddit_autorizado"
    with pytest.raises(ValueError, match="procedencia"):
        validate_prepared_corpus(frame)
    frame = prepared.copy()
    frame.loc[1, "id_comentario"] = frame.loc[0, "id_comentario"]
    with pytest.raises(ValueError, match="Identificadores"):
        validate_prepared_corpus(frame)


def test_pilot_is_blocked_even_with_case_and_whitespace_changes(prepared):
    cases = json.loads(KPI_PATH.read_text(encoding="utf-8"))
    frame = prepared.copy()
    frame.loc[0, "texto_limpio"] = "\n " + cases[0]["texto"].upper() + "  "
    with pytest.raises(ValueError, match="T001"):
        reject_kpi_overlap(frame)
    assert reject_kpi_overlap(prepared)["normalized_exact_overlap"] == 0


@pytest.mark.integracion
def test_export_is_blinded_pending_and_never_overwritten(tmp_path):
    folder = tmp_path / "review"
    report = export_for_review(folder)
    frame = pd.read_csv(folder / "corpus_para_anotar.csv")
    assert len(frame) == 72 and frame.etiqueta.isna().all()
    validate_prepared_corpus(frame, require_labels=False)
    template = pd.read_csv(folder / "plantilla_revision.csv")
    assert template.estado_revision.eq("pendiente").all()
    assert template[["evaluador", "fecha_revision", "justificacion"]].isna().all().all()
    assert report["reviewers"] == [] and report["human_approval_date"] is None
    for name, digest in report["files_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest
    assert "texto_original" not in frame
    with pytest.raises(FileExistsError):
        export_for_review(folder)


@pytest.mark.integracion
def test_preprocessing_cannot_overwrite_sidecar(tmp_path):
    csv, parquet = tmp_path/"data.csv", tmp_path/"data.parquet"
    sidecar = csv.with_suffix(".quality.json")
    sidecar.write_text("previous evidence")
    with pytest.raises(FileExistsError):
        process_and_save(output_csv=csv, output_parquet=parquet)
    assert sidecar.read_text() == "previous evidence"
    assert not csv.exists() and not parquet.exists()


@pytest.mark.integracion
def test_training_requires_explicit_synthetic_mode_and_existing_annotations(tmp_path, prepared):
    from train_models import run_training_pipeline
    path = tmp_path/"input.csv"
    prepared.to_csv(path, index=False)
    out = tmp_path/"run"
    with pytest.raises(ValueError, match="synthetic-mode"):
        run_training_pipeline(path, out)
    db = tmp_path/"missing.sqlite3"
    with pytest.raises(ValueError, match="base existente"):
        run_training_pipeline(path, out, annotation_db=db, synthetic_mode="reviewed")
    assert not out.exists() and not db.exists()


@pytest.mark.integracion
def test_training_cannot_accept_kpi_case(tmp_path, prepared):
    from train_models import run_training_pipeline
    frame = prepared.copy()
    frame.loc[0, "texto_limpio"] = json.loads(KPI_PATH.read_text(encoding="utf-8"))[0]["texto"]
    path = tmp_path/"input.csv"
    frame.to_csv(path, index=False)
    out = tmp_path/"run"
    with pytest.raises(ValueError, match="KPI"):
        run_training_pipeline(path, out, synthetic_mode="exploratory")
    assert not out.exists()


@pytest.mark.integracion
def test_reviewed_training_requires_complete_annotation_record(tmp_path, prepared):
    from annotations import AnnotationStore
    from train_models import run_training_pipeline
    path = tmp_path/"input.csv"
    prepared.to_csv(path, index=False)
    db = tmp_path/"empty.sqlite3"
    AnnotationStore(db)
    with pytest.raises(ValueError, match="dos anotaciones"):
        run_training_pipeline(path, tmp_path/"run", annotation_db=db, synthetic_mode="reviewed")


@pytest.mark.sistema
def test_exploratory_training_models_and_report_ui(tmp_path, prepared, monkeypatch):
    from train_models import run_training_pipeline
    from model_registry import load_run_model
    from streamlit.testing.v1 import AppTest
    path = tmp_path/"input.csv"
    prepared.to_csv(path, index=False)
    out = run_training_pipeline(path, tmp_path/"runs"/"exploratory", bootstrap_samples=10,
                                synthetic_mode="exploratory")
    report = json.loads((out/"run.json").read_text(encoding="utf-8"))
    assert report["evaluation_scope"] == "demostracion_tecnica_exploratoria"
    assert report["quality"]["review_status"] == "pendiente"
    assert sum(report["split_sizes"].values()) == 72
    parts = pd.read_csv(out/"partitions.csv")
    assert parts.id_comentario.nunique() == 72
    assert parts.groupby("id_hilo").partition.nunique().eq(1).all()
    for key in ["selected", "baseline", "logistic", "svm"]:
        model, _ = load_run_model(out, key)
        assert model.predict(["Gracias por compartir."])[0] in {"Odio", "Ofensivo", "Neutro"}
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(tmp_path/"history.sqlite3"))
    source = (Path(__file__).parents[1]/"app.py").read_text(encoding="utf-8")
    source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(tmp_path)!r})')
    app = AppTest.from_string(source, default_timeout=30).run()
    app.sidebar.selectbox[0].set_value("exploratory").run()
    assert not app.exception
    assert any("exploratoria" in msg.value for msg in app.info)
    app.text_area[0].set_value("Gracias por compartir.")
    app.button[0].click().run()
    assert not app.exception and app.metric[0].value in {"Odio", "Ofensivo", "Neutro"}
    app.sidebar.radio[0].set_value("Reportes").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 3


@pytest.mark.integracion
def test_reviewed_training_uses_database_labels_not_proposals(tmp_path, prepared):
    """Registros simulados exclusivos del test; nunca son revisión del equipo."""
    from annotations import AnnotationStore
    from train_models import run_training_pipeline
    frame = prepared.groupby("etiqueta", sort=False).head(6).copy()
    labels = dict(zip(frame.id_comentario, frame.etiqueta))
    frame["etiqueta"] = ""  # Mismo CSV sin propuestas que cargan los anotadores.
    path = tmp_path/"blinded.csv"
    frame.to_csv(path, index=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    db = tmp_path/"fixture_annotations.sqlite3"
    store = AnnotationStore(db)
    for unit, label in labels.items():
        for evaluator in ["FIXTURE_A", "FIXTURE_B"]:
            store.record(digest, unit, evaluator, label, "grupo simulado" if label == "Odio" else "",
                         "Registro simulado exclusivo de prueba automatizada")
    out = run_training_pipeline(path, tmp_path/"reviewed", bootstrap_samples=2,
                                annotation_db=db, synthetic_mode="reviewed")
    result = pd.read_csv(out/"corpus.csv")
    assert dict(zip(result.id_comentario, result.etiqueta)) == labels
    report = json.loads((out/"run.json").read_text(encoding="utf-8"))
    assert report["quality"]["review_status"] == "anotaciones_registradas_identidad_no_autenticada"
    assert report["source_sha256"] == digest
