import copy
import hashlib
import json

import pandas as pd
import pytest

from annotations import AnnotationStore


def corpus_fixture():
    frame = pd.DataFrame({
        "id_comentario": [f"u{i:03d}" for i in range(72)],
        "texto_limpio": [f"Texto fixture {i}" for i in range(72)],
    })
    content = frame.to_csv(index=False).encode("utf-8")
    return frame, content, hashlib.sha256(content).hexdigest()


def completed_package(tmp_path, role, disagree=False):
    frame, content, corpus_hash = corpus_fixture()
    store = AnnotationStore(tmp_path / f"local-{role}.sqlite3")
    code = f"FIXTURE-CODE-{role}"
    store.claim_role(corpus_hash, role, code)
    for index, unit in enumerate(frame.id_comentario):
        label = "Ofensivo" if disagree and index == 0 else "Neutro"
        store.record(corpus_hash, unit, code, label, "", "Justificación fixture", "2.0")
    return store, store.export_individual(corpus_hash, role, frame), frame, content, corpus_hash


def resign(package):
    body = {key: value for key, value in package.items() if key != "package_sha256"}
    package["package_sha256"] = hashlib.sha256(AnnotationStore._canonical_json(body)).hexdigest()
    return package


def test_individual_export_is_complete_and_private(tmp_path):
    store, package, frame, _, corpus_hash = completed_package(tmp_path, "A")
    assert package["role"] == "A"
    assert package["corpus_rows"] == 72 and len(package["annotations"]) == 72
    assert package["evaluator_pseudonym"].startswith("reviewer-")
    serialized = AnnotationStore.package_bytes(package).decode("utf-8")
    assert "FIXTURE-CODE-A" not in serialized
    assert "Texto fixture" not in serialized
    assert set(package["annotations"][0]) == {
        "comment_id", "class", "target_group", "justification", "manual_version", "annotated_at"
    }


def test_export_rejects_incomplete_review(tmp_path):
    frame, _, corpus_hash = corpus_fixture()
    store = AnnotationStore(tmp_path / "partial.sqlite3")
    store.claim_role(corpus_hash, "A", "FIXTURE-CODE-A")
    store.record(corpus_hash, frame.id_comentario.iloc[0], "FIXTURE-CODE-A", "Neutro", "", "Fixture")
    with pytest.raises(ValueError, match="72 comentarios"):
        store.export_individual(corpus_hash, "A", frame)


def test_consolidation_imports_a_and_b_without_touching_sources(tmp_path):
    store_a, package_a, frame, content, corpus_hash = completed_package(tmp_path, "A")
    store_b, package_b, _, _, _ = completed_package(tmp_path, "B", disagree=True)
    before_a, before_b = store_a.path.read_bytes(), store_b.path.read_bytes()
    central_path = tmp_path / "central.sqlite3"
    central = AnnotationStore.consolidate_packages(
        central_path, [package_b, package_a], content, frame
    )
    assert store_a.path.read_bytes() == before_a
    assert store_b.path.read_bytes() == before_b
    roles = central.reviewers(corpus_hash)
    assert set(roles) == {"A", "B"}
    assert all(value.startswith("reviewer-") for value in roles.values())
    assert central.review_completion(corpus_hash, frame.id_comentario.tolist())["complete"]
    annotations, decisions = central.tables(corpus_hash)
    assert len(annotations) == 144 and decisions.empty
    assert central.agreement(corpus_hash, roles["A"], roles["B"])["stage"] == "pre_adjudication"
    assert central.disagreements(corpus_hash)["all"] == ["u000"]


def test_consolidation_rejects_corrupt_package_without_creating_db(tmp_path):
    _, package_a, frame, content, _ = completed_package(tmp_path, "A")
    _, package_b, _, _, _ = completed_package(tmp_path, "B")
    package_a["package_sha256"] = "0" * 64
    destination = tmp_path / "central.sqlite3"
    with pytest.raises(ValueError, match="corrupto"):
        AnnotationStore.consolidate_packages(destination, [package_a, package_b], content, frame)
    assert not destination.exists()


def test_consolidation_rejects_invalid_counts_without_creating_db(tmp_path):
    _, package_a, frame, content, _ = completed_package(tmp_path, "A")
    _, package_b, _, _, _ = completed_package(tmp_path, "B")
    package_a["annotations"].append(copy.deepcopy(package_a["annotations"][0]))
    package_a["corpus_rows"] = 73
    resign(package_a)
    destination = tmp_path / "central.sqlite3"
    with pytest.raises(ValueError, match="exactamente 72"):
        AnnotationStore.consolidate_packages(destination, [package_a, package_b], content, frame)
    assert not destination.exists()


def test_consolidation_rejects_duplicate_ids_wrong_role_and_hash_mismatch(tmp_path):
    _, package_a, frame, content, _ = completed_package(tmp_path, "A")
    _, package_b, _, _, _ = completed_package(tmp_path, "B")

    duplicate = copy.deepcopy(package_a)
    duplicate["annotations"][1]["comment_id"] = duplicate["annotations"][0]["comment_id"]
    resign(duplicate)
    with pytest.raises(ValueError, match="duplicados"):
        AnnotationStore.consolidate_packages(tmp_path / "duplicate.sqlite3", [duplicate, package_b], content, frame)

    wrong_role = copy.deepcopy(package_a)
    wrong_role["role"] = "E3"
    resign(wrong_role)
    with pytest.raises(ValueError, match="rol incorrecto"):
        AnnotationStore.consolidate_packages(tmp_path / "role.sqlite3", [wrong_role, package_b], content, frame)

    changed_content = content + b"\n"
    with pytest.raises(ValueError, match="hash del corpus"):
        AnnotationStore.consolidate_packages(tmp_path / "hash.sqlite3", [package_a, package_b], changed_content, frame)


def test_consolidation_rejects_duplicate_role_and_existing_destination(tmp_path):
    _, package_a, frame, content, _ = completed_package(tmp_path, "A")
    _, package_b, _, _, _ = completed_package(tmp_path, "B")
    with pytest.raises(ValueError, match="rol A y uno del rol B"):
        AnnotationStore.consolidate_packages(tmp_path / "same-role.sqlite3", [package_a, package_a], content, frame)
    existing = tmp_path / "existing.sqlite3"
    existing.write_bytes(b"do-not-overwrite")
    with pytest.raises(FileExistsError, match="no se sobrescribe"):
        AnnotationStore.consolidate_packages(existing, [package_a, package_b], content, frame)
    assert existing.read_bytes() == b"do-not-overwrite"


def test_final_csv_requires_e3_and_only_real_disagreement(tmp_path):
    _, package_a, frame, content, corpus_hash = completed_package(tmp_path, "A")
    _, package_b, _, _, _ = completed_package(tmp_path, "B", disagree=True)
    central = AnnotationStore.consolidate_packages(
        tmp_path / "central.sqlite3", [package_a, package_b], content, frame
    )
    with pytest.raises(ValueError, match="adjudicador E3"):
        central.export(corpus_hash, frame)
    central.claim_role(corpus_hash, "E3", "FIXTURE-CODE-E3")
    with pytest.raises(ValueError, match="adjudicación"):
        central.export(corpus_hash, frame)
    with pytest.raises(ValueError, match="desacuerdos"):
        central.adjudicate(corpus_hash, "u001", "FIXTURE-CODE-E3", "Neutro", "", "No corresponde")
    central.adjudicate(corpus_hash, "u000", "FIXTURE-CODE-E3", "Neutro", "", "Decisión fixture")
    final = central.export(corpus_hash, frame)
    assert len(final) == 72 and final.loc[final.id_comentario == "u000", "etiqueta"].item() == "Neutro"
