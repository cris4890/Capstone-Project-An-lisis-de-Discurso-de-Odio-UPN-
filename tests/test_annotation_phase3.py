import pandas as pd
import pytest

from annotations import AnnotationStore


def test_roles_are_unique_and_persistent(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    store.claim_role("corpus", "A", "CODE-A")
    store.claim_role("corpus", "A", "CODE-A")
    with pytest.raises(ValueError, match="otro código"):
        store.claim_role("corpus", "A", "SECOND-A")
    with pytest.raises(ValueError, match="otro rol"):
        store.claim_role("corpus", "B", "CODE-A")
    assert store.reviewers("corpus") == {"A": "CODE-A"}


def test_independent_progress_and_resume(tmp_path):
    path = tmp_path / "annotations.sqlite3"
    first = AnnotationStore(path)
    first.record("corpus", "u1", "A", "Neutro", "", "No hay ataque")
    assert first.progress("corpus", "A", ["u1", "u2"])["completed"] == 1
    assert first.progress("corpus", "B", ["u1", "u2"])["completed"] == 0
    resumed = AnnotationStore(path)
    assert resumed.progress("corpus", "A", ["u1", "u2"]) == {
        "total": 2, "completed": 1, "pending": 1, "fraction": .5
    }


def test_only_real_disagreements_are_exposed_and_resolved(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    for role, code in [("A", "CODE-A"), ("B", "CODE-B"), ("E3", "CODE-E3")]:
        store.claim_role("corpus", role, code)
    for code in ["CODE-A", "CODE-B"]:
        store.record("corpus", "agreed", code, "Neutro", "", "Sin ataque")
    store.record("corpus", "disputed", "CODE-A", "Odio", "nacionalidad", "Ataque grupal")
    store.record("corpus", "disputed", "CODE-B", "Ofensivo", "", "Insulto individual")
    assert store.disagreements("corpus") == {
        "all": ["disputed"], "pending": ["disputed"], "resolved": []
    }
    with pytest.raises(ValueError, match="rol E3"):
        store.adjudicate("corpus", "disputed", "OTHER", "Odio", "nacionalidad", "Decisión")
    store.adjudicate("corpus", "disputed", "CODE-E3", "Odio", "nacionalidad", "Decisión final")
    assert store.disagreements("corpus")["pending"] == []


def test_export_requires_registered_pair_and_all_adjudications(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    for role, code in [("A", "CODE-A"), ("B", "CODE-B"), ("E3", "CODE-E3")]:
        store.claim_role("corpus", role, code)
    frame = pd.DataFrame({"id_comentario": ["u"], "texto_limpio": ["Texto"]})
    store.record("corpus", "u", "CODE-A", "Neutro", "", "Sin ataque")
    with pytest.raises(ValueError, match="roles A y B"):
        store.record("corpus", "u", "INTRUDER", "Neutro", "", "Sin ataque")
    with pytest.raises(ValueError, match="dos anotaciones"):
        store.export("corpus", frame)
    store.record("corpus", "u", "CODE-B", "Odio", "grupo", "Ataque")
    with pytest.raises(ValueError, match="adjudicación"):
        store.export("corpus", frame)
    store.adjudicate("corpus", "u", "CODE-E3", "Neutro", "", "Decisión final")
    assert store.export("corpus", frame).etiqueta.tolist() == ["Neutro"]


def test_agreement_is_explicitly_pre_adjudication(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    labels = ["Odio", "Ofensivo", "Neutro"]
    for index, label in enumerate(labels):
        for code in ["A", "B"]:
            store.record("corpus", str(index), code, label, "grupo" if label == "Odio" else "", "Razón")
    report = store.agreement("corpus", "A", "B")
    assert report["n"] == 3 and report["kappa"] == 1
    assert report["stage"] == "pre_adjudication"
