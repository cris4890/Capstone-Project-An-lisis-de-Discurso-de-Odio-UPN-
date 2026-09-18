"""
Aplicación Web de Moderación y Análisis de Discurso de Odio en Reddit
====================================================================

Proyecto: Análisis y Clasificación Automática del Discurso de Odio
          en Comunidades de Reddit (r/Millennials y r/GenZ) - Capstone UPN.

Módulos integrados:
1. Inferencia en tiempo real con preprocesamiento, medición de latencia y diseño UI/UX en 2 columnas.
2. Cuadro de mando de métricas comparativas y matrices de confusión (PC4).
3. Análisis exploratorio interactivo por comunidad (r/Millennials vs r/GenZ) con Plotly.

Autor: Senior UI/UX Designer & Full-Stack AI Engineer
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

# Módulos del proyecto local
from data_pipeline import clean_and_anonymize
from model_classes import (
    TARGET_CLASSES,
    RuleBasedClassifier,
    TransformerClassifier,
)

# Rutas estándar del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "corpus_preprocesado.csv"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"
METRICS_JSON_PATH = METRICS_DIR / "model_comparison.json"
BEST_MODEL_PATH = MODELS_DIR / "best_model.pkl"
BEST_MODEL_META_PATH = MODELS_DIR / "best_model_metadata.json"

# =====================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO PROFESIONAL (UI/UX)
# =====================================================================
st.set_page_config(
    page_title="Reddit Hate Speech Classifier - Capstone UPN",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyección de estilos CSS avanzados para una interfaz moderna, limpia y coherente
st.markdown(
    """
    <style>
    /* Suavizado general de bordes y tipografía */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Contenedores y tarjetas con bordes redondeados y sombras suaves */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px !important;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* Alertas con esquinas redondeadas */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    
    /* Campos de texto y selectores redondeados */
    div.stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    div.stTextArea textarea:focus {
        border-color: #ff4500 !important;
        box-shadow: 0 0 0 1px #ff4500 !important;
    }
    div.stSelectbox div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    /* Botón Primario estilizado con el color oficial Reddit Orange (#FF4500) */
    div.stButton > button[kind="primary"], div.stButton > button {
        background-color: #ff4500 !important;
        border-color: #ff4500 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.65rem 1.25rem !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 12px rgba(255, 69, 0, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #e03d00 !important;
        border-color: #e03d00 !important;
        box-shadow: 0 6px 16px rgba(255, 69, 0, 0.45) !important;
        transform: translateY(-2px) !important;
    }
    div.stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Tarjeta destacada de resultado */
    .result-card-odio {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1.5px solid #f87171;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.12);
        margin-bottom: 1rem;
    }
    .result-card-ofensivo {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1.5px solid #fbbf24;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.12);
        margin-bottom: 1rem;
    }
    .result-card-neutro {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1.5px solid #4ade80;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.12);
        margin-bottom: 1rem;
    }

    /* Badges de etiquetas */
    .badge-odio {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
    }
    .badge-ofensivo {
        background-color: #f59e0b;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
    }
    .badge-neutro {
        background-color: #10b981;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
    }
    
    /* Caja de texto anonimizado */
    .anonymized-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        font-family: 'Consolas', monospace;
        font-size: 0.92rem;
        color: #1e293b;
        line-height: 1.6;
        word-break: break-word;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# 2. FUNCIONES DE CARGA Y CACHÉ
# =====================================================================
@st.cache_data
def load_corpus() -> pd.DataFrame:
    """Carga el dataset tabular procesado."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    st.error("No se encontró el archivo de datos: 'data/corpus_preprocesado.csv'")
    return pd.DataFrame()


@st.cache_data
def load_metrics_data() -> Optional[Dict[str, Any]]:
    """Carga las métricas comparativas generadas en PC4."""
    if METRICS_JSON_PATH.exists():
        with open(METRICS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_resource
def load_model_by_name(model_choice: str) -> Tuple[Any, str, str]:
    """
    Carga el modelo seleccionado con caché para optimizar la latencia en inferencia.
    Retorna: (instancia_modelo, nombre_exacto_seleccionado, detalle_arquitectura)
    """
    if "Ganador" in model_choice:
        if BEST_MODEL_PATH.exists():
            model = joblib.load(BEST_MODEL_PATH)
            arch = "Línea Base Heurística (Mayor Macro-F1 en Test: 89.63%)"
            if BEST_MODEL_META_PATH.exists():
                with open(BEST_MODEL_META_PATH, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    arch = meta.get("best_model_name", arch)
            return model, model_choice, f"Artefacto Serializado ({arch})"
        return RuleBasedClassifier(), model_choice, "Línea Base (Fallback)"

    elif "Línea Base" in model_choice:
        path = MODELS_DIR / "model_baseline.pkl"
        if path.exists():
            return joblib.load(path), model_choice, "Lexicón Bilingüe + Expresiones Regulares"
        return RuleBasedClassifier(), model_choice, "Lexicón Bilingüe + Expresiones Regulares"

    elif "ML Clásico" in model_choice:
        path = MODELS_DIR / "model_tfidf.pkl"
        if path.exists():
            return joblib.load(path), model_choice, "TfidfVectorizer(ngram_range=(1,2)) + LinearSVC"
        return RuleBasedClassifier(), model_choice, "Línea Base (Fallback)"

    elif "Transformer" in model_choice:
        return (
            TransformerClassifier(model_name="prajjwal1/bert-tiny", num_epochs=1),
            model_choice,
            "BERT-Tiny (prajjwal1/bert-tiny, 4.4M params)",
        )

    return RuleBasedClassifier(), model_choice, "Línea Base Heurística"


# =====================================================================
# 3. BARRA LATERAL (SIDEBAR): NAVEGACIÓN Y CONFIGURACIÓN
# =====================================================================
st.sidebar.image("https://img.icons8.com/color/96/reddit.png", width=64)
st.sidebar.title("Reddit AI Moderator")
st.sidebar.caption("Capstone Project: Análisis de Discurso de Odio (UPN)")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegación:",
    [
        "🔍 Inferencia en Tiempo Real",
        "📊 Métricas & Comparación de Modelos",
        "👥 Análisis por Comunidad (r/Millennials vs r/GenZ)",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración del Motor")
selected_model_option = st.sidebar.selectbox(
    "Selecciona el Modelo de Inferencia:",
    [
        "🏆 Modelo Ganador (Producción)",
        "📏 Línea Base (Reglas/Lexicón)",
        "⚙️ ML Clásico (TF-IDF + LinearSVC)",
        "🤖 Transformer (bert-tiny)",
    ],
    index=0,
    help="Permite contrastar en caliente la salida de las distintas arquitecturas desarrolladas en la PC4.",
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Comunidades Monitoreadas:**\n"
    "- `r/Millennials`\n"
    "- `r/GenZ`\n\n"
    "**Categorías Evaluadas:**\n"
    "- 🔴 `Odio` (Hate Speech)\n"
    "- 🟡 `Ofensivo` (Tóxico / Insultos)\n"
    "- 🟢 `Neutro` (Seguro)"
)


# =====================================================================
# SECCIÓN 1: INFERENCIA EN TIEMPO REAL (REDISEÑO UI/UX EN 2 COLUMNAS)
# =====================================================================
if menu == "🔍 Inferencia en Tiempo Real":
    st.title("🔍 Inferencia en Tiempo Real y Moderación de Contenido")
    st.markdown(
        "Evalúa comentarios de Reddit en español o inglés con preprocesamiento automático, "
        "enmascaramiento de identidades (`[USER]`, `[URL]`) y clasificación multiclas."
    )

    # Cargar modelo en memoria manteniendo 100% de coherencia con el sidebar
    with st.spinner("Sincronizando motor seleccionado..."):
        model, active_display_name, architecture_info = load_model_by_name(selected_model_option)

    # Banner central dinámico que refleja con exactitud la opción activa
    st.info(
        f"⚡ **Motor Activo:** `{active_display_name}` &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**Arquitectura:** *{architecture_info}*"
    )

    # Banco de ejemplos representativos
    ejemplos: Dict[str, str] = {
        "-- Seleccionar un ejemplo predeterminado --": "",
        "🚨 Caso de Prueba: 'eres un tonto no sirves para nada bruto'": "eres un tonto no sirves para nada bruto",
        "Ejemplo 1 (Odio - ES - Millennials)": "Todos esos inmigrantes que vienen a quitarnos los empleos deberían ser expulsados a la fuerza. u/carlos_90 tiene razón, arruinan nuestro país.",
        "Ejemplo 2 (Ofensivo - ES - GenZ)": "Cállate la puta boca, eres un tonto no sirves para nada bruto. Cero rizz u/skibidi_clown 💀.",
        "Ejemplo 3 (Neutro - ES - Millennials)": "¿Alguien más recuerda pasar las tardes jugando con la Nintendo 64 y comiendo cereales? Qué buenos tiempos u/retro_gamer.",
        "Ejemplo 4 (Odio - EN - GenZ)": "Get these third-world illegal invaders out of our country before they turn every city into a ghetto u/genz_nationalist.",
        "Ejemplo 5 (Ofensivo - EN - Millennials)": "Shut your fucking mouth, you clueless corporate bootlicker. Nobody asked for your stupid opinion u/office_drone.",
        "Ejemplo 6 (Neutro - EN - GenZ)": "Actually no cap, learning how to cook simple meals saved me so much money living in the dorms 🍳.",
    }

    # Distribución en 2 columnas principales (Entrada vs. Resultados en vivo)
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("### 📝 Entrada de Comentario")
        ejemplo_elegido = st.selectbox(
            "Cargar ejemplo representativo:",
            list(ejemplos.keys()),
            help="Selecciona un comentario sintético bilingüe para probar el sistema rápidamente.",
        )

        texto_inicial = ejemplos[ejemplo_elegido] if ejemplo_elegido != "-- Seleccionar un ejemplo predeterminado --" else ""

        user_input = st.text_area(
            "Texto del Comentario de Reddit:",
            value=texto_inicial,
            height=145,
            placeholder="Escribe o pega un comentario de Reddit aquí (ej: 'Los inmigrantes u/usuario... https://link.com')",
        )

        ejecutar = st.button("🚀 Clasificar Contenido", type="primary", use_container_width=True)

    with col_output:
        st.markdown("### 🎯 Panel de Resultados en Vivo")

        if ejecutar:
            if not user_input.strip():
                st.warning("⚠️ Por favor, ingresa un comentario o selecciona un ejemplo predeterminado antes de clasificar.")
            else:
                # 1. Preprocesamiento y anonimización de texto
                texto_limpio = clean_and_anonymize(user_input)

                # 2. Inferencia con medición de latencia
                t_inicio = time.perf_counter()
                prediccion_raw = model.predict([texto_limpio])
                t_fin = time.perf_counter()
                latencia_ms = (t_fin - t_inicio) * 1000

                prediccion = prediccion_raw[0] if len(prediccion_raw) > 0 else "Neutro"

                # Parámetros visuales y operativos según clase detectada
                if prediccion == "Odio":
                    card_class = "result-card-odio"
                    badge_html = "<span class='badge-odio'>🔴 DISCURSO DE ODIO</span>"
                    moderation_title = "🛑 Acción Sugerida: Bloqueo Automático Inmediato"
                    moderation_desc = (
                        "El comentario infringe directamente las políticas de convivencia al contener lenguaje de odio, "
                        "deshumanización o ataques dirigidos a colectivos protegidos. **Recomendación:** Supresión inmediata "
                        "y sanción de cuenta."
                    )
                elif prediccion == "Ofensivo":
                    card_class = "result-card-ofensivo"
                    badge_html = "<span class='badge-ofensivo'>🟡 CONTENIDO OFENSIVO</span>"
                    moderation_title = "⚠️ Acción Sugerida: Advertencia / Flag para Moderador"
                    moderation_desc = (
                        "El comentario presenta agresividad verbal, descalificaciones o insultos directos sin necesariamente "
                        "atacar a un grupo protegido bajo normas de odio. **Recomendación:** Ocultar temporalmente y alertar a moderador humano."
                    )
                else:
                    card_class = "result-card-neutro"
                    badge_html = "<span class='badge-neutro'>🟢 CONTENIDO NEUTRO</span>"
                    moderation_title = "✅ Acción Sugerida: Publicación Aprobada"
                    moderation_desc = (
                        "El comentario no presenta transgresión de normas comunitarias ni patrones de hostigamiento. "
                        "**Recomendación:** Autorización de publicación regular."
                    )

                # Tarjeta destacada con el veredicto
                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div>{badge_html}</div>
                            <div style="font-size: 0.88rem; color: #475569; font-weight: 600;">
                                ⚡ Latencia: <strong>{latencia_ms:.2f} ms</strong>
                            </div>
                        </div>
                        <h4 style="margin: 0.5rem 0; font-size: 1.05rem; color: #0f172a;">{moderation_title}</h4>
                        <p style="margin: 0; font-size: 0.92rem; color: #334155; line-height: 1.5;">{moderation_desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Desglose de KPIs en micro-tarjetas
                k_col1, k_col2 = st.columns(2)
                with k_col1:
                    st.metric("Modelo Empleado", active_display_name.split()[1] if len(active_display_name.split()) > 1 else active_display_name)
                with k_col2:
                    st.metric("Tiempo de Respuesta", f"{latencia_ms:.2f} ms")

                # Visualización del texto procesado y anonimizado
                st.markdown("**Texto Anonimizado (`data_pipeline.py`):**")
                st.markdown(f"<div class='anonymized-box'>{texto_limpio}</div>", unsafe_allow_html=True)

                # Badges de entidades detectadas
                detected_entities = []
                if "[USER]" in texto_limpio:
                    detected_entities.append("👤 Usuario Enmascarado (`[USER]`)")
                if "[URL]" in texto_limpio:
                    detected_entities.append("🔗 Hipervínculo Sanitizado (`[URL]`)")

                if detected_entities:
                    st.caption("🛡️ Entidades protegidas: " + " &nbsp;|&nbsp; ".join(detected_entities))

        else:
            # Estado inicial amigable (Empty State)
            st.markdown(
                """
                <div style="border: 2px dashed #cbd5e1; border-radius: 10px; padding: 2.75rem 1.5rem; text-align: center; color: #64748b; background-color: #f8fafc;">
                    <div style="font-size: 2.75rem; margin-bottom: 0.75rem;">🛡️</div>
                    <h4 style="color: #334155; margin-bottom: 0.5rem; font-weight: 700;">Esperando Contenido para Moderar</h4>
                    <p style="font-size: 0.95rem; line-height: 1.5; margin: 0 auto; max-width: 380px;">
                        Ingresa un comentario o selecciona un caso de prueba en la columna izquierda y presiona 
                        <strong style="color: #ff4500;">Clasificar Contenido</strong> para visualizar el diagnóstico en tiempo real.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =====================================================================
# SECCIÓN 2: MÉTRICAS & COMPARACIÓN DE MODELOS
# =====================================================================
elif menu == "📊 Métricas & Comparación de Modelos":
    st.title("📊 Evaluación y Comparación de Modelos (Hitos PC4)")
    st.markdown(
        "Análisis comparativo de los tres enfoques de Machine Learning y NLP evaluados "
        "sobre el **mismo conjunto de prueba de retención (Test Set, N=11, estratificado)**."
    )

    metrics_data = load_metrics_data()

    if metrics_data is None:
        st.warning("No se encontró el archivo de métricas en `metrics/model_comparison.json`. Ejecuta `python train_models.py` primero.")
    else:
        results = metrics_data.get("results", [])
        df_metrics = pd.DataFrame(results)

        # Destacar modelo con mejor Macro-F1
        best_model_row = df_metrics.loc[df_metrics["macro_f1"].idxmax()]

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("🏆 Modelo Ganador", best_model_row["model_name"])
        with k2:
            st.metric("Macro-F1 Campeón", f"{best_model_row['macro_f1']:.2%}")
        with k3:
            st.metric("Accuracy Campeón", f"{best_model_row['accuracy']:.2%}")
        with k4:
            st.metric("Tasa Falsos Negativos (Odio)", f"{best_model_row['fnr_odio']:.2%}")

        st.markdown("---")
        st.subheader("📋 Matriz Comparativa de Rendimiento (Test Set)")

        # Formatear tabla para presentación ejecutiva
        display_df = df_metrics.copy()
        display_df = display_df.rename(
            columns={
                "model_name": "Modelo",
                "accuracy": "Accuracy",
                "macro_f1": "Macro-F1 ★",
                "precision_odio": "Precisión (Odio)",
                "recall_odio": "Recall (Odio)",
                "fnr_odio": "FNR Odio ⚠️",
                "f1_odio": "F1 (Odio)",
                "f1_ofensivo": "F1 (Ofensivo)",
                "f1_neutro": "F1 (Neutro)",
            }
        )

        for col in display_df.columns:
            if col != "Modelo":
                display_df[col] = display_df[col].apply(lambda v: f"{v:.2%}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.caption(
            "★ **Macro-F1**: Métrica principal de balance multiclas (promedio no ponderado de F1).\n"
            "⚠️ **FNR Odio (False Negative Rate)**: $FNR = 1.0 - Recall$. Crucial para seguridad: indica el porcentaje "
            "de comentarios de odio que el modelo dejó escapar."
        )

        # Visualizador de Matrices de Confusión
        st.markdown("---")
        st.subheader("🖼️ Matrices de Confusión por Modelo")

        matrix_tabs = st.tabs([
            "Línea Base (Reglas/Lexicón)",
            "ML Clásico (TF-IDF + LinearSVC)",
            "Transformer (bert-tiny)",
        ])

        matrix_files = [
            ("metrics/matrix_baseline.png", "Línea Base"),
            ("metrics/matrix_tfidf.png", "ML Clásico"),
            ("metrics/matrix_transformer.png", "Transformer"),
        ]

        for tab, (path_str, name) in zip(matrix_tabs, matrix_files):
            with tab:
                img_path = BASE_DIR / path_str
                if img_path.exists():
                    st.image(str(img_path), caption=f"Matriz de Confusión: {name}", width=540)
                else:
                    st.warning(f"Imagen no disponible en {path_str}")


# =====================================================================
# SECCIÓN 3: ANÁLISIS POR COMUNIDAD (r/Millennials vs r/GenZ)
# =====================================================================
elif menu == "👥 Análisis por Comunidad (r/Millennials vs r/GenZ)":
    st.title("👥 Análisis de Comunidades: r/Millennials vs r/GenZ")
    st.markdown(
        "Exploración de la distribución del corpus bilingüe preprocesado, contrastando "
        "las dinámicas discursivas observadas entre ambas generaciones."
    )

    df_corpus = load_corpus()

    if df_corpus.empty:
        st.warning("El corpus de datos no está disponible.")
    else:
        # Métricas agregadas
        total_regs = len(df_corpus)
        counts_etiqueta = df_corpus["etiqueta"].value_counts(normalize=True) * 100

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Registros", total_regs)
        with m2:
            st.metric("🔴 Proporción Odio", f"{counts_etiqueta.get('Odio', 0):.1f}%")
        with m3:
            st.metric("🟡 Proporción Ofensivo", f"{counts_etiqueta.get('Ofensivo', 0):.1f}%")
        with m4:
            st.metric("🟢 Proporción Neutro", f"{counts_etiqueta.get('Neutro', 0):.1f}%")

        st.markdown("---")

        # Paleta de colores estándar para consistencia
        color_map = {
            "Odio": "#ef4444",
            "Ofensivo": "#f59e0b",
            "Neutro": "#10b981",
        }

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Distribución por Subreddit")
            fig_sub = px.histogram(
                df_corpus,
                x="subreddit",
                color="etiqueta",
                barmode="group",
                color_discrete_map=color_map,
                labels={"subreddit": "Subreddit", "count": "Frecuencia", "etiqueta": "Clase"},
                title="Comportamiento del Discurso: r/Millennials vs r/GenZ",
            )
            fig_sub.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_sub, use_container_width=True)

        with col_g2:
            st.subheader("Distribución por Idioma")
            fig_lang = px.histogram(
                df_corpus,
                x="idioma",
                color="etiqueta",
                barmode="group",
                color_discrete_map=color_map,
                labels={"idioma": "Idioma", "count": "Frecuencia", "etiqueta": "Clase"},
                title="Comportamiento del Discurso por Idioma (ES vs EN)",
            )
            fig_lang.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_lang, use_container_width=True)

        # Explorador Interactivo de Datos
        st.markdown("---")
        st.subheader("🔎 Explorador Interactivo del Corpus")

        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            sub_filter = st.selectbox("Filtrar por Subreddit:", ["Todos"] + sorted(df_corpus["subreddit"].unique().tolist()))
        with f_col2:
            lang_filter = st.selectbox("Filtrar por Idioma:", ["Todos"] + sorted(df_corpus["idioma"].unique().tolist()))
        with f_col3:
            label_filter = st.selectbox("Filtrar por Etiqueta:", ["Todos"] + sorted(df_corpus["etiqueta"].unique().tolist()))
        with f_col4:
            search_query = st.text_input("Buscar término en texto:", placeholder="ej. inmigrantes, cringe...")

        df_filtered = df_corpus.copy()
        if sub_filter != "Todos":
            df_filtered = df_filtered[df_filtered["subreddit"] == sub_filter]
        if lang_filter != "Todos":
            df_filtered = df_filtered[df_filtered["idioma"] == lang_filter]
        if label_filter != "Todos":
            df_filtered = df_filtered[df_filtered["etiqueta"] == label_filter]
        if search_query.strip():
            df_filtered = df_filtered[
                df_filtered["texto_original"].str.contains(search_query, case=False, na=False)
                | df_filtered["texto_limpio"].str.contains(search_query, case=False, na=False)
            ]

        st.caption(f"Mostrando {len(df_filtered)} de {len(df_corpus)} comentarios.")
        st.dataframe(
            df_filtered[["id_comentario", "subreddit", "idioma", "etiqueta", "texto_limpio", "texto_original"]],
            use_container_width=True,
            height=300,
        )

        csv_download = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Subconjunto Filtrado (CSV)",
            data=csv_download,
            file_name="corpus_filtrado.csv",
            mime="text/csv",
        )
