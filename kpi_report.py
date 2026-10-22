"""Display preserved pilot evidence independently of the selected training run."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_pilot(root):
    directory = Path(root) / "docs" / "sprint2" / "evidencias"
    summary = json.loads((directory / "kpi.json").read_text(encoding="utf-8-sig"))
    cases = pd.read_csv(directory / "anexo_kpi.csv")
    required = {"id", "texto", "referencia", "manual_categoria", "manual_segundos", "hatedetect", "e2e_segundos"}
    if not required.issubset(cases.columns) or len(cases) != 30 or cases.id.nunique() != 30:
        raise ValueError("Anexo KPI incompleto o con identificadores duplicados.")
    for key, column in [("manual", "manual_categoria"), ("hatedetect", "hatedetect")]:
        correct = int((cases[column] == cases.referencia).sum())
        if correct != summary[key]["aciertos"] or abs(correct / len(cases) - summary[key]["exactitud"]) > 1e-9:
            raise ValueError("Los KPI no coinciden con el anexo de casos.")
    return directory, summary, cases


def render_kpi_report(root):
    st.subheader("KPI del piloto: manual vs. HateDetect")
    st.caption("Evidencia histórica de Sprint 2 · 30 comentarios sintéticos · Reglas de contexto v2. "
               "Ficha manual: 04/10/2026; medición del navegador: 19/10/2026.")
    st.info("Este piloto es independiente de la ejecución elegida en el menú y del Historial. "
            "Sus resultados no se recalculan al guardar comentarios ni al seleccionar otro modelo.")
    try:
        directory, summary, cases = load_pilot(root)
    except (OSError, ValueError, KeyError, TypeError):
        st.error("No se pudo verificar la evidencia KPI. Revise kpi.json y anexo_kpi.csv; no se muestran resultados estimados.")
        return
    manual, model = summary["manual"], summary["hatedetect"]
    left, right, third = st.columns(3)
    left.metric("Casos del piloto", len(cases))
    right.metric("Exactitud manual", f'{manual["exactitud"]:.2%}')
    third.metric("Exactitud HateDetect", f'{model["exactitud"]:.2%}')
    st.warning(summary["limitacion"])
    comparison = pd.DataFrame([
        {"Indicador": "Aciertos", "Manual": manual["aciertos"], "HateDetect": model["aciertos"]},
        {"Indicador": "Errores", "Manual": manual["errores"], "HateDetect": len(cases) - model["aciertos"]},
        {"Indicador": "Tiempo medio medido (segundos)", "Manual": manual["media_segundos"], "HateDetect": model["media_e2e_segundos"]},
        {"Indicador": "Tiempo total medido (segundos)", "Manual": manual["total_segundos"], "HateDetect": model["total_ventanas_segundos"]},
        {"Indicador": "Capacidad en ventanas medidas (textos/minuto)", "Manual": manual["textos_por_minuto"], "HateDetect": model["capacidad_ventanas_textos_minuto"]},
        {"Indicador": "Cobertura en 60 segundos (%)", "Manual": 100 * manual["cobertura_60s"], "HateDetect": 100 * model["cobertura_ventanas_60s"]},
    ])
    st.dataframe(comparison, hide_index=True, width="stretch")
    st.caption("Cobertura = casos procesados en 60 segundos / 30, en orden fijo; no equivale a recall. "
               "La capacidad se calcula sobre ventanas cronometradas, no sobre el flujo completo de trabajo.")
    with st.expander("Cómo se calcularon y qué limitaciones tienen"):
        st.markdown("Exactitud = aciertos / 30. Tiempo medio = tiempo total / 30. "
                    "Capacidad = 60 × 30 / tiempo total. El tiempo E2E va del clic al resultado renderizado; "
                    "excluye pegado del texto, revisión humana y guardado. La referencia procede de la ficha aportada; "
                    "no se acredita un estándar independiente. Se conservan las columnas originales D y J para auditoría.")
    st.write("Detalle de los 30 casos")
    st.dataframe(cases[["id", "texto", "referencia", "manual_categoria", "manual_segundos", "hatedetect", "e2e_segundos"]]
                 .rename(columns={"id": "ID", "texto": "Comentario", "referencia": "Referencia provisional",
                                  "manual_categoria": "Clasificación manual", "manual_segundos": "Manual (s)",
                                  "hatedetect": "HateDetect", "e2e_segundos": "HateDetect E2E (s)"}),
                 hide_index=True, width="stretch")
    st.download_button("Descargar detalle KPI (CSV)", (directory / "anexo_kpi.csv").read_bytes(),
                       file_name="anexo_kpi_30.csv", mime="text/csv", key="kpi_cases_download")
    st.download_button("Descargar indicadores KPI (JSON)", (directory / "kpi.json").read_bytes(),
                       file_name="kpi_piloto.json", mime="application/json", key="kpi_summary_download")
    st.caption("Fuente: docs/sprint2/evidencias/ · Protocolo: docs/sprint2/protocolo_kpi.md. Descargas en CSV/JSON; no PDF.")
