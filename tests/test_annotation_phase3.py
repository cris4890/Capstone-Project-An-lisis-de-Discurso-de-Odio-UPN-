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


def test_agreement_visibility_waits_for_both_registered_reviewers(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    store.claim_role("corpus", "A", "CODE-A")
    store.claim_role("corpus", "B", "CODE-B")
    units = ["u1", "u2"]
    for unit in units:
        store.record("corpus", unit, "CODE-A", "Neutro", "", "Sin ataque")
    store.record("corpus", "u1", "CODE-B", "Neutro", "", "Sin ataque")
    status = store.review_completion("corpus", units)
    assert status["complete"] is False
    assert status["reviewers"]["A"]["pending"] == 0
    assert status["reviewers"]["B"]["pending"] == 1
    store.record("corpus", "u2", "CODE-B", "Neutro", "", "Sin ataque")
    assert store.review_completion("corpus", units)["complete"] is True


def test_target_case_and_whitespace_are_consistent_everywhere(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.sqlite3")
    for role, code in [("A", "CODE-A"), ("B", "CODE-B"), ("E3", "CODE-E3")]:
        store.claim_role("corpus", role, code)
    store.record("corpus", "u", "CODE-A", "Odio", "Personas Migrantes", "Ataque grupal")
    store.record("corpus", "u", "CODE-B", "Odio", "  personas   migrantes  ", "Mismo grupo")
    assert store.disagreements("corpus")["all"] == []
    with pytest.raises(ValueError, match="desacuerdos"):
        store.adjudicate("corpus", "u", "CODE-E3", "Odio", "personas migrantes", "No corresponde")
    frame = pd.DataFrame({"id_comentario": ["u"], "texto_limpio": ["Texto"]})
    assert store.export("corpus", frame).etiqueta.tolist() == ["Odio"]


def test_registered_export_requires_a_and_b_but_legacy_pair_still_works(tmp_path):
    frame = pd.DataFrame({"id_comentario": ["u"], "texto_limpio": ["Texto"]})
    registered = AnnotationStore(tmp_path / "registered.sqlite3")
    registered.claim_role("corpus", "A", "CODE-A")
    registered.claim_role("corpus", "B", "CODE-B")
    registered.record("corpus", "u", "CODE-A", "Neutro", "", "Sin ataque")
    with pytest.raises(ValueError, match="dos anotaciones"):
        registered.export("corpus", frame)
    registered.record("corpus", "u", "CODE-B", "Neutro", "", "Sin ataque")
    assert registered.export("corpus", frame).etiqueta.tolist() == ["Neutro"]

    legacy = AnnotationStore(tmp_path / "legacy.sqlite3")
    for evaluator in ["PILOT-1", "PILOT-2"]:
        legacy.record("old-corpus", "u", evaluator, "Neutro", "", "Piloto anterior")
    assert legacy.export("old-corpus", frame).etiqueta.tolist() == ["Neutro"]
