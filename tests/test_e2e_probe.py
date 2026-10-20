from e2e_probe import enabled


def test_probe_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CAPSTONE_E2E", raising=False)
    assert not enabled()


def test_probe_requires_explicit_flag(monkeypatch):
    monkeypatch.setenv("CAPSTONE_E2E", "true")
    assert not enabled()
    monkeypatch.setenv("CAPSTONE_E2E", "1")
    assert enabled()
