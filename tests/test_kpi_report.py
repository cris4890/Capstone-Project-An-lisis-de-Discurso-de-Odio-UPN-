import json
import shutil
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from kpi_report import load_pilot

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integracion
def test_pilot_summary_matches_30_cases():
    _, summary, cases = load_pilot(ROOT)
    assert len(cases) == 30
    assert summary["manual"]["aciertos"] == 28
    assert summary["hatedetect"]["aciertos"] == 18
    assert summary["hatedetect"]["exactitud"] == .6
    assert summary["comparacion_causal_valida"] is False


@pytest.mark.integracion
def test_inconsistent_summary_is_rejected(tmp_path):
    directory = tmp_path / "docs/sprint2/evidencias"
    directory.mkdir(parents=True)
    for name in ["kpi.json", "anexo_kpi.csv"]:
        shutil.copy(ROOT / "docs/sprint2/evidencias" / name, directory / name)
    summary = json.loads((directory / "kpi.json").read_text(encoding="utf-8"))
    summary["hatedetect"]["aciertos"] = 30
    (directory / "kpi.json").write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(ValueError, match="no coinciden"):
        load_pilot(tmp_path)


@pytest.mark.sistema
def test_kpi_tab_available_without_training_or_history(tmp_path, monkeypatch):
    history = tmp_path / "history.sqlite3"
    monkeypatch.setenv("CAPSTONE_HISTORY_DB", str(history))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.sidebar.radio[0].set_value("Reportes").run()
    assert not app.exception
    assert "KPI del piloto" in [tab.label for tab in app.tabs]
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Exactitud HateDetect"] == "60.00%"
    assert metrics["Exactitud manual"] == "93.33%"
    assert not history.exists()


@pytest.mark.sistema
def test_missing_kpi_shows_error_not_fake_results(tmp_path):
    def render(root):
        from kpi_report import render_kpi_report
        render_kpi_report(root)
    app = AppTest.from_function(render, args=(str(tmp_path),)).run()
    assert not app.exception
    assert app.error and not app.metric
