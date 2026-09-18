# 🛡️ Reddit Hate Speech Classifier — Capstone UPN

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4500.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow.svg)](https://huggingface.co/)

Sistema integral de moderación automática, clasificación multiclas y análisis exploratorio del discurso de odio en comunidades de Reddit (`r/Millennials` y `r/GenZ`), desarrollado para el proyecto de **Capstone - Universidad Privada del Norte (UPN)**.

---

## 📌 Descripción del Proyecto

Las plataformas sociales albergan diversas dinámicas intergeneracionales donde convergen slang, tensiones sociopolíticas y expresiones polarizantes. Este proyecto implementa un pipeline completo de NLP que:

1. **Anonimiza y normaliza** menciones de usuarios (`u/usuario` $\to$ `[USER]`), enlaces (`https://...` $\to$ `[URL]`) y codificación Unicode preservando emojis y signos clave.
2. **Clasifica** comentarios en tres categorías éticas y de moderación:
   - 🔴 **Odio (Hate Speech)**: Ataques o deshumanización dirigidos a grupos protegidos (nacionalidad, orientación sexual, raza, religión).
   - 🟡 **Ofensivo (Toxicity/Insults)**: Agresividad verbal, vulgaridad e insultos directos sin atacar minorías protegidas.
   - 🟢 **Neutro**: Discusiones constructivas, nostalgia, preguntas informativas o comentarios seguros.
3. **Compara tres familias de modelos (Hitos PC4)**:
   - **Modelo 1**: Línea Base Heurística (Lexicón bilingüe y reglas regex).
   - **Modelo 2**: Machine Learning Clásico (TF-IDF + `LinearSVC` / `LogisticRegression`).
   - **Modelo 3**: Deep Learning Transformer (Fine-tuning de `prajjwal1/bert-tiny` con PyTorch).
4. **Despliega un Dashboard Interactivo en Streamlit**: Inferencia en tiempo real en dos columnas, métricas comparativas y análisis visual de comunidades con Plotly Express.

---

## 📂 Estructura del Repositorio

```text
Capstone-/
├── data/
│   ├── corpus_preprocesado.csv          # Dataset tabular procesado (UTF-8)
│   └── corpus_preprocesado.parquet      # Dataset columnar optimizado (PyArrow)
├── models/
│   ├── best_model.pkl                   # Modelo serializado campeón para producción
│   ├── best_model_metadata.json         # Metadatos del modelo ganador
│   ├── model_baseline.pkl               # Modelo de Línea Base (Reglas/Lexicón)
│   └── model_tfidf.pkl                  # Pipeline TF-IDF + Clasificador Lineal
├── metrics/
│   ├── matrix_baseline.png              # Matriz de confusión: Línea Base
│   ├── matrix_tfidf.png                 # Matriz de confusión: ML Clásico
│   ├── matrix_transformer.png           # Matriz de confusión: Transformer BERT-Tiny
│   └── model_comparison.json            # Reporte de KPIs comparativos (PC4)
├── model_classes.py                     # Definición modular de estimadores y datasets PyTorch
├── data_pipeline.py                     # Generación de corpus, anonimización y guardado
├── train_models.py                      # Partición estratificada, entrenamiento y evaluación
├── app.py                               # Dashboard web interactivo en Streamlit
├── requirements.txt                     # Lista de dependencias del entorno
├── .gitignore                           # Exclusiones de Git (entornos, temporales, cachés)
└── README.md                            # Documentación general del proyecto
```

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto localmente:

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/capstone-reddit-nlp.git
cd capstone-reddit-nlp
```

### 2. Crear y Activar un Entorno Virtual

- **En Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

- **En Linux / macOS (Bash/Zsh)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🧪 Ejecución de Módulos (Flujo Completo)

### Paso A: Preprocesamiento y Generación de Datos (Opcional)
Si deseas regenerar el corpus sintético bilingüe y ejecutar la anonimización:
```bash
python data_pipeline.py
```

### Paso B: Reentrenamiento y Evaluación de Modelos (Hitos PC4)
Ejecuta la partición estratificada (70% Train, 15% Val, 15% Test), entrena los 3 modelos, calcula los KPIs y genera las matrices de confusión:
```bash
python train_models.py
```

### Paso C: Iniciar la Aplicación Web (Streamlit)
Lanza el panel de moderación y visualización interactiva:
```bash
streamlit run app.py
```

Abre tu navegador en: [http://localhost:8501](http://localhost:8501)

---

## 📊 Resumen Comparativo de Modelos (Evaluación Test Set)

Evaluación realizada sobre exactamente la misma partición de prueba no vista ($N = 11$, estratificado con semilla fija `42`):

| Modelo | Accuracy | Macro-F1 ★ | Precisión (Odio) | Recall (Odio) | FNR (Odio) ⚠️ | F1 (Odio) | F1 (Ofensivo) | F1 (Neutro) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Línea Base (Reglas/Lexicón)** 🏆 | **90.91%** | **89.63%** | **100.00%** | **66.67%** | **33.33%** | **80.00%** | **100.00%** | **88.89%** |
| **ML Clásico (TF-IDF + LR/SVC)** | 54.55% | 48.15% | 33.33% | 66.67% | 33.33% | 44.44% | 100.00% | 0.00% |
| **Transformer (`bert-tiny`)** | 27.27% | 24.44% | 28.57% | 66.67% | 33.33% | 40.00% | 33.33% | 0.00% |

> **Nota sobre KPIs de Moderación**:
> - **Macro-F1 (Criterio Rector)**: Evalúa el balance equitativo entre las tres clases sin sesgo de frecuencias.
> - **FNR Odio (False Negative Rate)**: $FNR = 1.0 - \text{Recall}$. Métrica crítica de seguridad que mide qué proporción de contenido de odio escapó a los filtros del modelo.

---

## 💻 Uso en Producción / Inferencia con Python

Puedes cargar el modelo entrenado y clasificar nuevos textos directamente:

```python
import joblib
from data_pipeline import clean_and_anonymize

# 1. Cargar el modelo ganador de producción
model = joblib.load("models/best_model.pkl")

# 2. Entrada cruda con menciones y enlaces
comentario = "Todos esos inmigrantes deben ser expulsados u/usuario https://noticia.com"

# 3. Anonimizar y clasificar
comentario_limpio = clean_and_anonymize(comentario)
prediccion = model.predict([comentario_limpio])[0]

print(f"Predicción: {prediccion}")  # Salida: 'Odio'
```

---

## 👥 Créditos Académicos

- **Institución**: Universidad Privada del Norte (UPN)
- **Proyecto**: Capstone — Clasificación Automática de Discurso de Odio en Reddit
- **Entorno**: Python 3.10+ | Scikit-Learn | PyTorch | Hugging Face Transformers | Streamlit
