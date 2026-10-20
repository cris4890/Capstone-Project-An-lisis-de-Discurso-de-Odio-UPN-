"""Instrumentación optativa de laboratorio; no mide solo model.predict."""
import os
from pathlib import Path


def enabled():
    return os.environ.get("CAPSTONE_E2E") == "1"


def render_probe():
    if enabled():
        import streamlit.components.v1 as components
        components.html(Path(__file__).with_name("e2e_probe.html").read_text(encoding="utf-8"), height=190)
