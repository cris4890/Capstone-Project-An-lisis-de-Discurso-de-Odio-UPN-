"""
Módulo de Entrenamiento, Evaluación y Comparación de Modelos de NLP (PC4)
========================================================================

Proyecto: Análisis y Clasificación Automática del Discurso de Odio
          en Comunidades de Reddit (r/Millennials y r/GenZ).

Este módulo implementa el flujo experimental exigido en la PC4:
1. Partición estricta y estratificada (Train 70%, Val 15%, Test 15%) fijando semilla.
2. Tres arquitecturas contrastantes:
   - Modelo 1: Línea Base Heurística basada en Reglas y Lexicón Bilingüe.
   - Modelo 2: Machine Learning Clásico (TF-IDF + Selección entre Logistic Regression y LinearSVC).
   - Modelo 3: Deep Learning con Transformer Ligero (Fine-tuning de BERT-Tiny en PyTorch).
3. Evaluación estandarizada sobre el conjunto de prueba idéntico, calculando KPIs clave:
   - Accuracy, Macro-F1, F1 por clase.
   - Precisión de Odio, Recall de Odio y Tasa de Falsos Negativos (FNR) de Odio.
4. Generación de matrices de confusión visuales (.png) y reporte de métricas (.json).
5. Serialización del modelo ganador para consumo en inferencia/producción.

Autor: Senior ML & NLP Engineer
"""

import copy
import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from model_classes import (
    TARGET_CLASSES,
    RuleBasedClassifier,
    TransformerClassifier,
)

# Configuración de variables de entorno para suprimir advertencias no críticas
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuración de logging profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("TrainModelsPC4")

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "corpus_preprocesado.parquet"
MODELS_DIR = BASE_DIR / "models"
METRICS_DIR = BASE_DIR / "metrics"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42

# Fijar semillas para reproducibilidad
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)


@dataclass
class ModelMetrics:
    """Estructura de datos para almacenar los KPIs de evaluación."""
    model_name: str
    accuracy: float
    macro_f1: float
    precision_odio: float
    recall_odio: float
    fnr_odio: float
    f1_odio: float
    f1_ofensivo: float
    f1_neutro: float


# =====================================================================
# 1. PARTICIÓN ESTRATIFICADA DE DATOS
# =====================================================================
def load_and_split_data(
    data_path: Union[str, Path] = DATA_PATH,
    random_state: int = RANDOM_SEED,
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Carga el corpus preprocesado y genera particiones estrictas y reproducibles:
    70% Entrenamiento, 15% Validación y 15% Prueba, estratificando por etiqueta.

    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test
    """
    logger.info("Cargando corpus preprocesado desde: %s", data_path)
    df = pd.read_parquet(data_path)

    # Priorizar la columna con normalización y anonimización de texto
    text_col = "texto_limpio" if "texto_limpio" in df.columns else "texto_original"
    X = df[text_col]
    y = df["etiqueta"]

    # Paso 1: Separar 70% Entrenamiento y 30% Temporal (Val + Test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=random_state, stratify=y
    )

    # Paso 2: Dividir el 30% temporal al 50% para obtener 15% Val y 15% Test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=random_state, stratify=y_temp
    )

    logger.info("Partición completada con éxito:")
    logger.info(
        " - Train: %d muestras (%.1f%%) -> Clases: %s",
        len(X_train),
        len(X_train) / len(df) * 100,
        y_train.value_counts().to_dict(),
    )
    logger.info(
        " - Val:   %d muestras (%.1f%%) -> Clases: %s",
        len(X_val),
        len(X_val) / len(df) * 100,
        y_val.value_counts().to_dict(),
    )
    logger.info(
        " - Test:  %d muestras (%.1f%%) -> Clases: %s",
        len(X_test),
        len(X_test) / len(df) * 100,
        y_test.value_counts().to_dict(),
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


# =====================================================================
# 2. MODELO 2: MACHINE LEARNING CLÁSICO (TF-IDF + LR / LinearSVC)
# =====================================================================
def train_classic_ml(
    X_train: pd.Series,
    y_train: pd.Series,
    X_val: pd.Series,
    y_val: pd.Series,
) -> Tuple[Pipeline, str, float]:
    """
    Entrena y compara modelos lineales clásicos con extracción de características TF-IDF:
    1. TF-IDF + LogisticRegression(class_weight='balanced')
    2. TF-IDF + LinearSVC(class_weight='balanced')

    Selecciona el mejor estimador según el Macro-F1 obtenido en la partición de Validación.
    """
    logger.info("Entrenando candidatos de ML Clásico (LogisticRegression vs LinearSVC)...")

    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        strip_accents="unicode",
        lowercase=True,
    )

    candidates: Dict[str, Pipeline] = {
        "TF-IDF + LogisticRegression": Pipeline([
            ("tfidf", copy.deepcopy(tfidf)),
            (
                "clf",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                    max_iter=1000,
                ),
            ),
        ]),
        "TF-IDF + LinearSVC": Pipeline([
            ("tfidf", copy.deepcopy(tfidf)),
            (
                "clf",
                LinearSVC(
                    C=0.8,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                    max_iter=2000,
                ),
            ),
        ]),
    }

    best_name = ""
    best_macro_f1 = -1.0
    best_pipeline: Optional[Pipeline] = None

    for name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        y_val_pred = pipeline.predict(X_val)
        val_macro_f1 = f1_score(y_val, y_val_pred, average="macro", zero_division=0)
        logger.info(" - %s -> Macro-F1 (Val): %.4f", name, val_macro_f1)

        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
            best_name = name
            best_pipeline = pipeline

    assert best_pipeline is not None
    logger.info("Ganador ML Clásico en Validación: %s (Macro-F1: %.4f)", best_name, best_macro_f1)
    return best_pipeline, best_name, best_macro_f1


# =====================================================================
# 3. EVALUACIÓN, KPIs DE PC4 Y GENERACIÓN DE MATRICES DE CONFUSIÓN
# =====================================================================
def evaluate_model_on_test(
    model: Any,
    model_name: str,
    X_test: pd.Series,
    y_test: pd.Series,
    confusion_matrix_path: Path,
) -> ModelMetrics:
    """
    Evalúa un modelo en el conjunto de prueba idéntico, calculando:
    - Accuracy general
    - Precision de Odio
    - Recall de Odio
    - F1-score por cada clase ('Odio', 'Ofensivo', 'Neutro')
    - Macro-F1
    - Tasa de Falsos Negativos (FNR) de Odio: FN / (TP + FN)

    Además genera y persiste la matriz de confusión formateada en PNG.
    """
    y_pred = model.predict(X_test)

    # 1. KPIs Globales y por Clase
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    # Precisión y Recall para la clase crítica 'Odio'
    prec_odio = precision_score(y_test, y_pred, labels=["Odio"], average=None, zero_division=0)[0]
    rec_odio = recall_score(y_test, y_pred, labels=["Odio"], average=None, zero_division=0)[0]

    # F1 por clase en orden contractual
    f1_classes = f1_score(y_test, y_pred, labels=TARGET_CLASSES, average=None, zero_division=0)
    f1_odio, f1_ofensivo, f1_neutro = f1_classes[0], f1_classes[1], f1_classes[2]

    # Tasa de Falsos Negativos de Odio (FNR = 1.0 - Recall)
    total_odio_real = np.sum(y_test == "Odio")
    fn_odio = np.sum((y_test == "Odio") & (y_pred != "Odio"))
    fnr_odio = float(fn_odio / total_odio_real) if total_odio_real > 0 else 0.0

    metrics = ModelMetrics(
        model_name=model_name,
        accuracy=float(acc),
        macro_f1=float(macro_f1),
        precision_odio=float(prec_odio),
        recall_odio=float(rec_odio),
        fnr_odio=float(fnr_odio),
        f1_odio=float(f1_odio),
        f1_ofensivo=float(f1_ofensivo),
        f1_neutro=float(f1_neutro),
    )

    # 2. Generación y Guardado de Matriz de Confusión Visual
    cm = confusion_matrix(y_test, y_pred, labels=TARGET_CLASSES)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=TARGET_CLASSES,
        yticklabels=TARGET_CLASSES,
        cbar=False,
        linewidths=1.0,
        linecolor="gray",
    )
    plt.title(f"Matriz de Confusión\n{model_name} (Macro-F1: {macro_f1:.2%})", fontsize=12, pad=12)
    plt.xlabel("Etiqueta Predicha", fontsize=11)
    plt.ylabel("Etiqueta Real", fontsize=11)
    plt.tight_layout()
    plt.savefig(confusion_matrix_path, dpi=300)
    plt.close()
    logger.info("Matriz de confusión guardada en: %s", confusion_matrix_path)

    return metrics


def display_comparison_table(results: List[ModelMetrics]) -> None:
    """Imprime una tabla formateada en consola con la comparativa de los 3 modelos."""
    header = (
        f"{'Modelo':<32} | {'Accuracy':<9} | {'Macro-F1':<9} | {'Prec(Odio)':<10} | "
        f"{'Rec(Odio)':<10} | {'FNR(Odio)':<10} | {'F1(Odio)':<9} | {'F1(Ofens)':<9} | {'F1(Neut)':<9}"
    )
    separator = "-" * len(header)
    print("\n" + "=" * len(header))
    print("RESUMEN COMPARATIVO DE RENDIMIENTO EN CONJUNTO DE PRUEBA (PC4)")
    print("=" * len(header))
    print(header)
    print(separator)
    for m in results:
        print(
            f"{m.model_name:<32} | {m.accuracy:>8.2%} | {m.macro_f1:>8.2%} | {m.precision_odio:>9.2%} | "
            f"{m.recall_odio:>9.2%} | {m.fnr_odio:>9.2%} | {m.f1_odio:>8.2%} | {m.f1_ofensivo:>8.2%} | {m.f1_neutro:>8.2%}"
        )
    print("=" * len(header) + "\n")


# =====================================================================
# 4. PIPELINE PRINCIPAL DE ENTRENAMIENTO Y PERSISTENCIA
# =====================================================================
def run_training_pipeline() -> None:
    """Coordina todo el ciclo de entrenamiento, evaluación, comparación y persistencia."""
    logger.info("=== INICIANDO PIPELINE DE ENTRENAMIENTO Y COMPARACIÓN PC4 ===")

    # 1. Cargar y particionar datos
    X_train, X_val, X_test, y_train, y_val, y_test = load_and_split_data()

    # 2. Configurar Modelo 1 (Reglas / Lexicón)
    logger.info("Configurando Modelo 1: Línea Base por Reglas/Lexicón...")
    model_baseline = RuleBasedClassifier()

    # 3. Entrenar y seleccionar Modelo 2 (ML Clásico)
    best_classic_pipe, classic_name, _ = train_classic_ml(X_train, y_train, X_val, y_val)

    # 4. Entrenar Modelo 3 (Transformer Bert-Tiny)
    logger.info("Entrenando Modelo 3: Transformer Ligero (bert-tiny)...")
    model_transformer = TransformerClassifier(
        model_name="prajjwal1/bert-tiny",
        num_epochs=8,
        batch_size=8,
        lr=1.2e-4,
    )
    model_transformer.fit(X_train, y_train, X_val, y_val)

    # 5. Evaluar los 3 modelos sobre la partición idéntica de Prueba
    logger.info("Evaluando los 3 modelos sobre la partición de prueba (N=%d)...", len(X_test))

    m1_metrics = evaluate_model_on_test(
        model=model_baseline,
        model_name="Línea Base (Reglas/Lexicón)",
        X_test=X_test,
        y_test=y_test,
        confusion_matrix_path=METRICS_DIR / "matrix_baseline.png",
    )

    m2_metrics = evaluate_model_on_test(
        model=best_classic_pipe,
        model_name=f"ML Clásico ({classic_name})",
        X_test=X_test,
        y_test=y_test,
        confusion_matrix_path=METRICS_DIR / "matrix_tfidf.png",
    )

    m3_metrics = evaluate_model_on_test(
        model=model_transformer,
        model_name="Transformer (bert-tiny)",
        X_test=X_test,
        y_test=y_test,
        confusion_matrix_path=METRICS_DIR / "matrix_transformer.png",
    )

    results = [m1_metrics, m2_metrics, m3_metrics]
    display_comparison_table(results)

    # 6. Guardar archivo comparativo en JSON
    json_path = METRICS_DIR / "model_comparison.json"
    comparison_data = {
        "kpis_description": {
            "fnr_odio": "Tasa de Falsos Negativos de Odio: casos de odio que el modelo no detectó (menor es mejor)",
            "macro_f1": "Media no ponderada de F1 entre clases (criterio principal de selección)",
        },
        "test_partition_size": len(X_test),
        "results": [asdict(m) for m in results],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=4, ensure_ascii=False)
    logger.info("Comparativa de modelos guardada en: %s", json_path)

    # 7. Selección y Persistencia del Mejor Modelo
    best_result = max(results, key=lambda x: x.macro_f1)
    logger.info(
        "★ MODELO GANADOR: '%s' con Macro-F1 de %.2f%% y FNR(Odio) de %.2f%%",
        best_result.model_name,
        best_result.macro_f1 * 100,
        best_result.fnr_odio * 100,
    )

    best_model_obj: Any = None
    if "Línea Base" in best_result.model_name:
        best_model_obj = model_baseline
    elif "ML Clásico" in best_result.model_name:
        best_model_obj = best_classic_pipe
    else:
        best_model_obj = model_transformer

    # Guardar también modelos individuales para que app.py los consuma directamente
    joblib.dump(model_baseline, MODELS_DIR / "model_baseline.pkl")
    joblib.dump(best_classic_pipe, MODELS_DIR / "model_tfidf.pkl")

    # Persistencia estandarizada del modelo ganador para consumo directo
    best_model_path = MODELS_DIR / "best_model.pkl"
    joblib.dump(best_model_obj, best_model_path)
    logger.info("Mejor modelo serializado exitosamente en: %s", best_model_path)

    # Metadatos del artefacto
    metadata_path = MODELS_DIR / "best_model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "best_model_name": best_result.model_name,
                "target_classes": TARGET_CLASSES,
                "macro_f1": best_result.macro_f1,
                "accuracy": best_result.accuracy,
                "fnr_odio": best_result.fnr_odio,
                "model_file": str(best_model_path.name),
            },
            f,
            indent=4,
            ensure_ascii=False,
        )
    logger.info("Metadatos del modelo guardados en: %s", metadata_path)
    logger.info("=== PIPELINE FINALIZADO CON ÉXITO ===")


if __name__ == "__main__":
    run_training_pipeline()
