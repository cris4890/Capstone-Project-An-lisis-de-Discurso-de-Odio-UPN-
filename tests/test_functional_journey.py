"""Functional journeys using isolated history and existing synthetic reports."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_save_search_and_filter_history(tmp_path, monkeypatch):
    from history_store import HistoryStore
    path = tmp_path / "history.sqlite3"
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(path))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.button[0].click().run()
    assert app.warning[0].value == "Ingrese un texto para analizar."
    assert not path.exists()
    app.text_area[0].set_value("Prueba funcional: gracias por compartir.")
    app.checkbox[0].check()
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "Neutro"
    assert len(HistoryStore(path).read()) == 1
    app.sidebar.radio[0].set_value("Historial").run()
    assert len(app.dataframe[0].value) == 1
    app.text_input[0].set_value("Prueba funcional").run()
    assert len(app.dataframe[0].value) == 1
    category = next(w for w in app.selectbox if w.label == "Filtrar por categoría")
    category.set_value("Odio").run()
    assert not app.exception and app.dataframe[0].value.empty
    next(w for w in app.selectbox if w.label == "Filtrar por categoría").set_value("Todas").run()
    app.text_input[0].set_value("inexistente_998877").run()
    assert not app.exception and app.dataframe[0].value.empty
    assert len(HistoryStore(path).read()) == 1


def test_corpus_filters_and_literal_search(tmp_path, monkeypatch):
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(tmp_path / "unused.sqlite3"))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.sidebar.radio[0].set_value("Reportes").run()
    next(w for w in app.selectbox if w.label == "Comunidad").set_value("r/GenZ").run()
    next(w for w in app.selectbox if w.label == "Idioma").set_value("es").run()
    frame = next(d.value for d in app.dataframe if "subreddit" in d.value.columns)
    assert not frame.empty
    assert set(frame.subreddit) == {"r/GenZ"} and set(frame.idioma) == {"es"}
    next(w for w in app.text_input if w.label == "Buscar texto").set_value("[inexistente_998877").run()
    assert not app.exception
    assert next(d.value for d in app.dataframe if "subreddit" in d.value.columns).empty
