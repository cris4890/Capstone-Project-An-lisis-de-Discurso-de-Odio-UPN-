import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from annotations import AnnotationStore, aiken_v
from corpus import prepare_corpus
from data_pipeline import clean_and_anonymize, generate_synthetic_data
from experiment import split_corpus, select_model, metrics_for, bootstrap_intervals
from model_registry import load_run_model


@pytest.fixture
def corpus():
    return prepare_corpus(generate_synthetic_data())[0]


def test_minimization_and_context():
    text = "No odio #respeto 👨‍👩‍👧‍👦 u/persona https://example.com persona@example.com +51 999 123 456"
    cleaned = clean_and_anonymize(text)
    assert "No odio #respeto 👨‍👩‍👧‍👦" in cleaned
    for token in ["[USER]", "[URL]", "[EMAIL]", "[PHONE]"]:
        assert token in cleaned
    assert "example.com" not in cleaned and "999" not in cleaned


def test_prepare_excludes_raw_and_deduplicates():
    raw = generate_synthetic_data()
    raw = pd.concat([raw, raw.iloc[:1]], ignore_index=True)
    raw["extra_secret"] = "private"
    prepared, quality = prepare_corpus(raw)
    assert len(prepared) == 72 and quality["removed_rows"] == 1
    assert not {"texto_original", "extra_secret"} & set(prepared)
    assert prepared.id_comentario.is_unique
    assert prepared.id_hilo.str.len().eq(36).all()


def test_real_data_requires_evidence():
    raw = generate_synthetic_data()
    raw["origen"] = "reddit_autorizado"
    with pytest.raises(ValueError, match="Procedencia"):
        prepare_corpus(raw)


def test_group_split_reproducible(corpus):
    # Dos comentarios distintos del mismo hilo deben quedar juntos.
    corpus.loc[1, "id_hilo"] = corpus.loc[0, "id_hilo"]
    a, b = split_corpus(corpus), split_corpus(corpus)
    assert sum(map(len,a.values())) == len(corpus)
    seen = set()
    for key, frame in a.items():
        assert not seen & set(frame.id_hilo)
        seen |= set(frame.id_hilo)
        assert set(frame.etiqueta) == {"Odio", "Ofensivo", "Neutro"}
        assert frame.id_comentario.tolist() == b[key].id_comentario.tolist()


def test_duplicates_cannot_leak(corpus):
    corpus.loc[1, "texto_limpio"] = corpus.loc[0, "texto_limpio"]
    with pytest.raises(ValueError, match="duplicados"):
        split_corpus(corpus)


def test_selection_uses_validation_only():
    assert select_model({"a": .8, "b": .3}) == "a"
    with pytest.raises(ValueError):
        select_model({"a": float("nan")})


def test_metrics_counts_and_missing_class():
    report = metrics_for(["Odio", "Odio", "Neutro"], ["Odio", "Neutro", "Odio"])
    assert report["per_class"]["Odio"]["fn"] == 1
    assert report["per_class"]["Odio"]["fp"] == 1
    assert report["per_class"]["Odio"]["fnr"] == .5
    assert report["per_class"]["Ofensivo"]["fnr"] is None
    assert report["missing_classes"] == ["Ofensivo"]


def test_bootstrap_deterministic(corpus):
    a = bootstrap_intervals(corpus, corpus.etiqueta, samples=20)
    b = bootstrap_intervals(corpus, corpus.etiqueta, samples=20)
    assert a == b
    assert a["macro_f1"]["low"] == 1


def test_anotations_and_adjudication(tmp_path):
    store = AnnotationStore(tmp_path/"a.sqlite3")
    frame = pd.DataFrame({"id_comentario": ["unit"], "texto_limpio": ["Texto"]})
    store.record("corpus", "unit", "A", "Neutro", "", "Sin ataque")
    with pytest.raises(ValueError):
        store.record("corpus", "unit", "A", "Neutro", "", "Repetida")
    with pytest.raises(ValueError):
        store.export("corpus",frame)
    store.record("corpus", "unit", "B", "Odio", "nacionalidad", "Ataque")
    with pytest.raises(ValueError):
        store.adjudicate("corpus", "unit", "A", "Neutro", "", "Decisión")
    with pytest.raises(ValueError):
        store.export("corpus",frame)
    store.adjudicate("corpus", "unit", "C", "Neutro", "", "Es una cita de denuncia")
    assert store.export("corpus",frame).etiqueta.tolist() == ["Neutro"]
    assert store.agreement("corpus", "A", "B")["kappa"] == 0


def test_kappa_perfect_and_aiken(tmp_path):
    store = AnnotationStore(tmp_path/"a.sqlite3")
    for i, label in enumerate(["Neutro", "Odio", "Ofensivo"]):
        for evaluator in ["A", "B"]:
            store.record("c", str(i), evaluator, label, "grupo", "razón")
    assert store.agreement("c", "A", "B")["kappa"] == 1
    assert aiken_v([[5,5,5], [1,1,1]]) == [1,0]


def test_registry_does_not_fallback(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_run_model(tmp_path,"transformer")
    (tmp_path/"run.json").write_text(json.dumps({"models":{},"selected_model":"transformer"}))
    with pytest.raises(FileNotFoundError):
        load_run_model(tmp_path,"selected")


def test_transformer_local_training_roundtrip(tmp_path):
    import torch
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from transformers import PreTrainedTokenizerFast, XLMRobertaConfig, XLMRobertaForSequenceClassification
    from model_classes import TransformerClassifier, TARGET_CLASSES
    base = tmp_path/"tiny-local"
    tokenizer = Tokenizer(WordLevel({"[UNK]":0,"[PAD]":1,"hello":2,"idiot":3,"attack":4}, unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    fast = PreTrainedTokenizerFast(tokenizer_object=tokenizer, unk_token="[UNK]", pad_token="[PAD]")
    fast.save_pretrained(base)
    config = XLMRobertaConfig(vocab_size=5,hidden_size=8,num_hidden_layers=1,num_attention_heads=2,
                             intermediate_size=16,max_position_embeddings=132,pad_token_id=1,num_labels=3,
                             id2label=dict(enumerate(TARGET_CLASSES)),label2id={c:i for i,c in enumerate(TARGET_CLASSES)})
    XLMRobertaForSequenceClassification(config).save_pretrained(base)
    model = TransformerClassifier(model_name=str(base),num_epochs=1,batch_size=3)
    with pytest.raises(RuntimeError):
        model.predict(["hello"])
    x = pd.Series(["attack", "idiot", "hello"])
    y = pd.Series(TARGET_CLASSES)
    model.fit(x,y,x,y)
    expected = model.predict_proba(x)
    model.save(tmp_path/"trained")
    restored = TransformerClassifier.load(tmp_path/"trained")
    np.testing.assert_allclose(restored.predict_proba(x),expected,rtol=1e-5)
    assert restored.predict([]).shape == (0,)
    np.testing.assert_allclose(expected.sum(axis=1),1,rtol=1e-5)


def test_streamlit_default_and_sections(tmp_path, monkeypatch):
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(tmp_path/"history.sqlite3"))
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).parents[1]/"app.py"),default_timeout=30).run()
    assert not app.exception
    app.text_area[0].set_value("Hola, gracias por ayudar.")
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "Neutro"
    for section in ["Reportes", "Historial"]:
        app.sidebar.radio[0].set_value(section).run()
        assert not app.exception


def test_adjudication_overrides_initial_consensus(tmp_path):
    store = AnnotationStore(tmp_path/"a.sqlite3")
    for evaluator in ["A", "B"]:
        store.record("c", "u", evaluator, "Ofensivo", "", "Insulto")
    store.adjudicate("c", "u", "C", "Neutro", "", "Cita para denunciar")
    frame = pd.DataFrame({"id_comentario":["u"], "texto_limpio":["Texto"]})
    assert store.export("c",frame).etiqueta.iloc[0] == "Neutro"


def test_language_review_blocks_training(corpus):
    corpus.loc[0, "revision_idioma"] = True
    with pytest.raises(ValueError,match="idioma"):
        split_corpus(corpus)


def test_valid_manifest_and_timezone_dates(tmp_path):
    evidence = tmp_path/"evidence.txt"
    evidence.write_text("TEST FIXTURE ONLY. Not a real authorization.")
    manifest = {"fuente":"test", "referencia":"fixture", "fecha_autorizacion":"2025-01-01T00:00:00Z",
                "alcance":"test", "conservacion_hasta":"2099-01-01T00:00:00Z", "responsable":"test",
                "evidencia_archivo":str(evidence), "fecha_inicio":"2025-01-01T00:00:00Z",
                "fecha_fin":"2026-12-31T23:59:59Z", "permite_entrenamiento":True}
    raw = generate_synthetic_data().iloc[:2].copy()
    raw["origen"] = "reddit_autorizado"
    raw["fecha"] = "2026-01-01T12:00:00Z"
    prepared, report = prepare_corpus(raw,manifest)
    assert len(prepared) == 2 and report["authorization_evidence_sha256"]
    manifest["permite_entrenamiento"] = False
    with pytest.raises(ValueError):
        prepare_corpus(raw,manifest)


def test_training_run_does_not_overwrite(tmp_path):
    from train_models import run_training_pipeline
    with pytest.raises(FileExistsError):
        run_training_pipeline(output=tmp_path)



def test_history_roundtrip_minimizes_data(tmp_path):
    from history_store import HistoryStore
    path = tmp_path/"history.sqlite3"
    store = HistoryStore(path)
    assert store.read().empty and not path.exists()
    store.add("Hola u/alguien persona@example.com", "Neutro", "Reglas", "demo", .2)
    records = HistoryStore(path).read()
    assert len(records) == 1
    assert records.iloc[0].text == "Hola [USER] [EMAIL]"
    assert pd.isna(records.iloc[0].confidence)
    with pytest.raises(ValueError):
        store.add("Hola", "Neutro", "Reglas", "demo", .2, 1.5)
    assert len(store.read()) == 1


def test_three_subsystems_and_optional_history(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from history_store import HistoryStore
    path = tmp_path/"history.sqlite3"
    monkeypatch.setenv("CAPSTONE_HISTORY_DB",str(path))
    app = AppTest.from_file(str(Path(__file__).parents[1]/"app.py"),default_timeout=30).run()
    assert app.sidebar.radio[0].options == ["Clasificación", "Reportes", "Historial"]
    app.text_area[0].set_value("Gracias u/ejemplo")
    app.button[0].click().run()
    assert not path.exists()
    app.checkbox[0].check()
    app.button[0].click().run()
    assert not app.exception
    assert len(HistoryStore(path).read()) == 1
    app.sidebar.radio[0].set_value("Historial").run()
    assert not app.exception and len(app.dataframe[0].value) == 1
    assert app.dataframe[0].value.iloc[0]["Texto procesado"] == "Gracias [USER]"
    app.sidebar.radio[0].set_value("Reportes").run()
    assert not app.exception and len(HistoryStore(path).read()) == 1
    assert [t.label for t in app.tabs] == ["Evaluación de modelos", "Exploración del corpus", "Anotación y acuerdo"]


def test_internal_annotation_separate():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).parents[1]/"annotation_app.py"),default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Anotación independiente"
    assert len(app.get("file_uploader")) == 1


def test_corrupt_history_is_reported_without_overwrite(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    path = tmp_path / "broken.sqlite3"
    original = b"not a sqlite database"
    path.write_bytes(original)
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(path))
    app = AppTest.from_file(str(Path(__file__).parents[1]/"app.py"), default_timeout=30).run()
    app.sidebar.radio[0].set_value("Historial").run()
    assert not app.exception
    assert "No se pudo leer" in app.error[0].value
    assert path.read_bytes() == original


def test_invalid_run_can_return_to_demo(tmp_path):
    from streamlit.testing.v1 import AppTest
    run = tmp_path / "runs" / "invalid"
    run.mkdir(parents=True)
    (run / "run.json").write_text('{broken', encoding="utf-8")
    source = (Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
    source = source.replace('ROOT = Path(__file__).resolve().parent', f'ROOT = Path({str(tmp_path)!r})')
    app = AppTest.from_string(source, default_timeout=30).run()
    app.sidebar.selectbox[0].set_value("invalid").run()
    assert not app.exception
    assert "No se pudo verificar" in app.error[0].value
    app.sidebar.selectbox[0].set_value("Demostración de reglas").run()
    assert not app.exception and app.text_area
