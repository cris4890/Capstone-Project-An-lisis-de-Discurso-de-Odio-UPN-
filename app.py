"""Panel local de investigación y revisión humana del discurso de odio."""
import json
import sqlite3
from pathlib import Path
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from history_store import HistoryStore, history_path
from corpus import SAFE_COLUMNS
from data_pipeline import clean_and_anonymize, generate_synthetic_data
from model_classes import RuleBasedClassifier
from model_registry import load_run_model

ROOT = Path(__file__).resolve().parent
st.set_page_config(
    page_title="Reddit Hate Speech Classifier - Capstone UPN",
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


@st.cache_resource
def load_model(run_directory, key):
    return load_run_model(run_directory, key)


def read_run(directory):
    return json.loads((directory / "run.json").read_text(encoding="utf-8"))


st.sidebar.title("Análisis de discurso de odio")
st.sidebar.caption("Capstone UPN · Apoyo a la revisión humana")
runs = sorted([p for p in (ROOT/"runs").glob("*") if (p/"run.json").is_file()], reverse=True)
choice = st.sidebar.selectbox("Ejecución", ["Demostración de reglas"] + [p.name for p in runs])
run_dir = next((p for p in runs if p.name == choice), None)
report = read_run(run_dir) if run_dir else None
menu = st.sidebar.radio("Sección", ["Clasificación", "Reportes", "Historial"])
st.sidebar.divider()
st.sidebar.caption("Herramienta de apoyo. La decisión final corresponde a una persona.")
if menu != "Historial" and (report is None or report["origin"] == "sintetico"):
    st.caption("● DATOS SINTÉTICOS · Demostración académica; no representa la prevalencia del odio en Reddit.")
elif menu != "Historial":
    st.info("Corpus declarado de origen real. Consulte su autorización y límites de muestreo antes de interpretar resultados.")

if menu == "Clasificación":
    st.title("Clasificación")
    st.write("Analiza un comentario y revisa su clasificación en español o inglés.")
    if report:
        options = ["selected"] + list(report["models"])
        key = st.selectbox("Modelo", options, format_func=lambda k: "Seleccionado por validación" if k == "selected" else report["models"][k]["name"])
        try:
            model, name = load_model(str(run_dir), key)
        except Exception as exc:
            st.error(f"No se pudo cargar el modelo seleccionado: {exc}")
            st.stop()
    else:
        model, name = RuleBasedClassifier(), "Línea base de reglas · Demostración"
    st.caption(f"Modelo activo: {name}")
    if isinstance(model, RuleBasedClassifier):
        with st.expander("Alcance y limitaciones del modelo"):
            st.write("Las reglas pueden confundir menciones neutrales, negaciones o citas con ataques. Revise siempre el contexto.")
    text = st.text_area("Comentario a analizar", height=170, placeholder="Escribe o pega aquí un comentario…")
    save_history = st.checkbox("Guardar en Historial", value=False,
        help="Guarda el texto procesado en este equipo. Revisa que no contenga información personal; el enmascaramiento automático no la detecta toda.")
    if st.button("Clasificar", type="primary"):
        cleaned = clean_and_anonymize(text)
        if not cleaned:
            st.warning("Ingrese un texto para analizar.")
        else:
            start = time.perf_counter()
            predicted = model.predict([cleaned])[0]
            elapsed = (time.perf_counter()-start)*1000
            st.subheader("Resultado del análisis")
            left, right = st.columns(2)
            left.metric("Predicción", predicted)
            right.metric("Tiempo de respuesta", f"{elapsed:.2f} ms")
            st.caption("Clasificación orientativa. Revisa el contexto antes de tomar una decisión.")
            confidence = None
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba([cleaned])[0]
                confidence = float(probabilities[list(model.classes_).index(predicted)])
                st.dataframe(pd.DataFrame({"Clase": model.classes_, "Probabilidad del modelo": probabilities}), hide_index=True)
                st.caption("Probabilidades sin calibración verificada; no equivalen a certeza.")
            else:
                st.caption("Este modelo no ofrece un porcentaje de confianza.")
            st.write("Texto procesado")
            st.code(cleaned, language=None)
            if save_history:
                try:
                    HistoryStore(history_path()).add(cleaned, str(predicted), name,
                        run_dir.name if run_dir else "demostracion_reglas", elapsed, confidence)
                    st.success("Clasificación guardada en Historial.")
                except (OSError, ValueError, sqlite3.Error):
                    st.error("La clasificación se realizó, pero no se pudo guardar en Historial.")

elif menu == "Reportes":
    st.title("Reportes")
    evaluation_tab, corpus_tab = st.tabs(["Evaluación de modelos", "Exploración del corpus"])
    with evaluation_tab:
        st.subheader("Evaluación de modelos")
        if report is None:
            st.info("Seleccione una ejecución completa. Los resultados antiguos permanecen conservados en metrics/ y no se presentan como una evaluación nueva.")
        else:
            st.write(f"Modelo seleccionado con validación: **{report['models'][report['selected_model']]['name']}**")
            st.write("Tamaños de las particiones", report["split_sizes"])
            if not report["transformer_included"]:
                st.warning("Esta ejecución no incluye entrenamiento del Transformer. La comparación del PC4 está incompleta.")
            columns = ["model_name", "validation_macro_f1", "macro_f1", "balanced_accuracy", "precision_odio", "recall_odio", "fnr_odio", "latency_ms_per_text"]
            st.dataframe(pd.DataFrame(report["results"])[columns], hide_index=True)
            for result in report["results"]:
                with st.expander(result["model_name"]):
                    st.image(str(run_dir/f"matrix_{result['key']}.png"))
                    st.write("Métricas por clase", pd.DataFrame(result["per_class"]).T)
                    st.write("Intervalos del 95 % por remuestreo de hilos", result["bootstrap_95"])
                    st.write("Pruebas funcionales", result["functional"])
                    group = st.selectbox("Desagregar por", list(result["subgroups"]), key=f"group_{result['key']}")
                    st.json(result["subgroups"][group])
                    errors = pd.read_csv(run_dir/f"errors_{result['key']}.csv")
                    st.write("Errores del conjunto de prueba", errors)
                    st.download_button("Descargar errores", errors.to_csv(index=False), file_name=f"errors_{result['key']}.csv", key=f"download_{result['key']}")
            for limitation in report["limitations"]:
                st.caption(limitation)

    with corpus_tab:
        st.subheader("Exploración del corpus")
        if run_dir:
            frame = pd.read_csv(run_dir/"corpus.csv")
        else:
            frame = generate_synthetic_data()
            frame["texto_limpio"] = frame.texto_original.apply(clean_and_anonymize)
        frame = frame[[c for c in SAFE_COLUMNS if c in frame]].copy()
        st.caption("Las comunidades no acreditan la edad ni la generación de las personas. Los gráficos describen este corpus.")
        community = st.selectbox("Comunidad", ["Todas"] + sorted(frame.subreddit.unique()))
        language = st.selectbox("Idioma", ["Todos"] + sorted(frame.idioma.unique()))
        if community != "Todas":
            frame = frame[frame.subreddit == community]
        if language != "Todos":
            frame = frame[frame.idioma == language]
        query = st.text_input("Buscar texto")
        if query:
            frame = frame[frame.texto_limpio.str.contains(query, case=False, regex=False, na=False)]
        st.metric("Registros", len(frame))
        st.plotly_chart(px.histogram(frame, x="subreddit", color="etiqueta", barmode="group"), width="stretch")
        st.dataframe(frame, hide_index=True)
        st.download_button("Descargar datos minimizados", frame.to_csv(index=False), file_name="corpus_minimizado.csv")

else:
    st.title("Historial")
    st.write("Consulta las clasificaciones que decidiste guardar en este equipo.")
    st.caption("Se conserva el texto procesado, la predicción y el modelo utilizado. Estos registros no son etiquetas validadas para entrenamiento.")
    records = HistoryStore(history_path()).read()
    if records.empty:
        st.info("Todavía no hay clasificaciones guardadas. Activa Guardar en Historial al analizar un comentario.")
    else:
        label = st.selectbox("Filtrar por categoría", ["Todas", "Odio", "Ofensivo", "Neutro"])
        if label != "Todas":
            records = records[records.prediction == label]
        search = st.text_input("Buscar en los textos guardados")
        if search:
            records = records[records.text.str.contains(search, case=False, regex=False, na=False)]
        st.caption(f"{len(records)} registros · Fechas en UTC")
        st.dataframe(records.rename(columns={"created_at":"Fecha UTC", "text":"Texto procesado", "prediction":"Categoría",
            "model_name":"Modelo", "run_id":"Ejecución", "confidence":"Probabilidad sin calibración verificada",
            "latency_ms":"Tiempo (ms)", "id":"Identificador"}), hide_index=True, width="stretch")
