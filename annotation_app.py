"""Herramienta interna de anotación, separada del sistema principal."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from annotations import AnnotationStore
from corpus import SAFE_COLUMNS
from data_pipeline import clean_and_anonymize
ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Anotación interna - Capstone UPN",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Los componentes heredan los colores del tema de Streamlit (claro u oscuro).
st.markdown(
    """
    <style>
    [data-testid="stMainBlockContainer"] {
        max-width: 1200px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    [data-testid="stSidebar"] h1 { font-size: 1.35rem; line-height: 1.35; }
    h1 { letter-spacing: -0.035em; }
    [data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        color: inherit;
        border: 1px solid rgba(128, 128, 128, 0.28);
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        min-height: 116px;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] div {
        color: inherit;
    }
    [data-testid="stMetricLabel"] { opacity: 0.85; }
    [data-testid="stMetricValue"] { font-weight: 650; }
    [data-testid="stAlert"] { border-radius: 10px; }
    [data-testid="stTextArea"] textarea {
        border-radius: 10px;
        font-size: 1rem;
        line-height: 1.65;
        padding: 1rem;
    }
    [data-testid="stTextArea"] textarea:focus-visible {
        outline: 2px solid #de5932;
        outline-offset: 2px;
    }
    [data-testid="stBaseButton-primary"] {
        background: #b93813;
        border-color: #b93813;
        color: #fff;
        min-height: 44px;
        padding: 0.65rem 1.5rem;
        border-radius: 9px;
        font-weight: 600;
    }
    [data-testid="stBaseButton-primary"]:hover {
        background: #992e10;
        border-color: #992e10;
        color: #fff;
    }
    [data-testid="stBaseButton-primary"]:focus-visible {
        outline: 2px solid #de5932;
        outline-offset: 3px;
    }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 2rem; }
        [data-testid="stMetric"] { min-height: 96px; padding: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("Herramienta interna")
st.sidebar.caption("Preparación del corpus · Equipo de investigación")

st.title("Anotación independiente")
st.caption("Uso local con evaluadores identificados por códigos. La identidad no se autentica; no publique este panel con datos restringidos.")
st.markdown("Manual: consulte **docs/manual_anotacion.md**, versión 1.0 pendiente de validación por especialistas.")
uploaded = st.file_uploader("Corpus minimizado para anotar (CSV)", type=["csv"])
if uploaded is None:
    st.info("Cargue un corpus preparado con identificadores internos. Cada evaluador verá el texto sin las etiquetas de los demás.")
    st.stop()
content = uploaded.getvalue()
corpus_hash = hashlib.sha256(content).hexdigest()
frame = pd.read_csv(uploaded, dtype={"id_comentario": str})
if not {"id_comentario", "texto_limpio"}.issubset(frame) or frame.id_comentario.duplicated().any():
    st.error("Se requieren identificadores únicos y texto_limpio.")
    st.stop()
frame = frame[[c for c in SAFE_COLUMNS if c in frame]].copy()
frame["texto_limpio"] = frame.texto_limpio.apply(clean_and_anonymize)
store = AnnotationStore(ROOT/"private"/"annotations.sqlite3")
evaluator = st.text_input("Código de evaluador")
mode = st.radio("Actividad", ["Anotar", "Adjudicar", "Acuerdo y exportación"])
annotations, decisions = store.tables(corpus_hash)
if mode == "Anotar":
    completed = set(annotations[annotations.evaluator == evaluator.strip()].unit)
    full = set(annotations.groupby("unit").size().loc[lambda x: x >= 2].index)
    pending = frame[~frame.id_comentario.isin(completed | full)]
    if pending.empty:
        st.success("No hay unidades pendientes para este evaluador.")
    else:
        unit = st.selectbox("Unidad", pending.id_comentario.tolist())
        st.write(pending.set_index("id_comentario").loc[unit, "texto_limpio"])
        with st.form("annotation"):
            label = st.selectbox("Clase", ["Odio", "Ofensivo", "Neutro"])
            target = st.text_input("Grupo o atributo atacado (obligatorio para Odio)")
            reason = st.text_area("Justificación")
            if st.form_submit_button("Guardar anotación"):
                try:
                    store.record(corpus_hash, unit, evaluator, label, target, reason)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
elif mode == "Adjudicar":
    # Solo unidades completas; no revelar una primera anotación a otro anotador.
    counts = annotations.groupby("unit").size()
    units = [u for u in counts[counts == 2].index if u not in set(decisions.unit)]
    if not units:
        st.info("No hay unidades con dos anotaciones pendientes de decisión.")
    else:
        unit = st.selectbox("Unidad para adjudicar", units)
        rows = annotations[annotations.unit == unit]
        if not evaluator.strip() or evaluator.strip() in set(rows.evaluator):
            st.info("Ingrese el código de un tercer evaluador.")
        else:
            st.write(frame.set_index("id_comentario").loc[unit, "texto_limpio"])
            st.dataframe(rows[["evaluator", "label", "target", "reason"]], hide_index=True)
            with st.form("decision"):
                label = st.selectbox("Clase final", ["Odio", "Ofensivo", "Neutro"])
                target = st.text_input("Grupo objetivo final")
                reason = st.text_area("Justificación de la adjudicación")
                if st.form_submit_button("Guardar decisión"):
                    try:
                        store.adjudicate(corpus_hash, unit, evaluator, label, target, reason)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
else:
    evaluators = sorted(annotations.evaluator.unique())
    if len(evaluators) >= 2:
        a = st.selectbox("Evaluador A", evaluators)
        b = st.selectbox("Evaluador B", [e for e in evaluators if e != a])
        agreement = store.agreement(corpus_hash,a,b)
        st.json(agreement)
        st.download_button("Descargar informe de acuerdo", json.dumps(agreement, ensure_ascii=False, indent=2), file_name="acuerdo.json")
    try:
        final = store.export(corpus_hash,frame)
        st.download_button("Descargar corpus anotado", final.to_csv(index=False), file_name="corpus_anotado.csv")
    except ValueError as exc:
        st.info(str(exc))
