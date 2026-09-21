"""Registro local de anotación independiente y adjudicación con auditoría."""
from contextlib import closing, contextmanager
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from data_pipeline import clean_and_anonymize

CLASSES = ["Odio", "Ofensivo", "Neutro"]


class AnnotationStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS annotations (
                corpus TEXT, unit TEXT, evaluator TEXT, label TEXT, target TEXT,
                reason TEXT, manual_version TEXT, created TEXT,
                PRIMARY KEY(corpus,unit,evaluator));
            CREATE TABLE IF NOT EXISTS decisions (
                corpus TEXT, unit TEXT, evaluator TEXT, label TEXT, target TEXT,
                reason TEXT, created TEXT, PRIMARY KEY(corpus,unit));
            """)

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.path)) as conn:
            with conn:
                yield conn

    def record(self, corpus, unit, evaluator, label, target, reason, manual_version="1.0"):
        self.validate(label, target, reason)
        if not all(str(x).strip() for x in [corpus, unit, evaluator, manual_version]):
            raise ValueError("Complete identificadores y versión del manual.")
        with self.connect() as conn:
            count = conn.execute("SELECT count(*) FROM annotations WHERE corpus=? AND unit=?", (corpus,unit)).fetchone()[0]
            if count >= 2:
                raise ValueError("La unidad ya tiene dos evaluaciones; corresponde adjudicar.")
            try:
                conn.execute("INSERT INTO annotations VALUES (?,?,?,?,?,?,?,?)",
                             (corpus,unit,evaluator.strip(),label,clean_and_anonymize(target),
                              clean_and_anonymize(reason),manual_version,datetime.now(timezone.utc).isoformat()))
            except sqlite3.IntegrityError as exc:
                raise ValueError("El evaluador ya registró esta unidad; no se sobrescribe la evidencia.") from exc

    @staticmethod
    def validate(label, target, reason):
        if label not in CLASSES or not str(reason).strip():
            raise ValueError("Seleccione una clase y justifique la decisión.")
        if label == "Odio" and not str(target).strip():
            raise ValueError("Registre el grupo o atributo objetivo del ataque.")

    def adjudicate(self, corpus, unit, evaluator, label, target, reason):
        self.validate(label,target,reason)
        with self.connect() as conn:
            rows = conn.execute("SELECT evaluator FROM annotations WHERE corpus=? AND unit=?", (corpus,unit)).fetchall()
            if len(rows) != 2 or not evaluator.strip() or evaluator.strip() in {r[0] for r in rows}:
                raise ValueError("La adjudicación requiere dos anotaciones y un tercer evaluador.")
            try:
                conn.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)",
                             (corpus,unit,evaluator.strip(),label,clean_and_anonymize(target),
                              clean_and_anonymize(reason),datetime.now(timezone.utc).isoformat()))
            except sqlite3.IntegrityError as exc:
                raise ValueError("Ya existe una decisión para esta unidad.") from exc

    def tables(self, corpus):
        with self.connect() as conn:
            return tuple(pd.read_sql_query("SELECT * FROM " + table + " WHERE corpus=?", conn, params=[corpus])
                         for table in ["annotations", "decisions"])

    def agreement(self, corpus, evaluator_a, evaluator_b):
        if evaluator_a == evaluator_b:
            raise ValueError("Seleccione dos evaluadores distintos.")
        annotations, _ = self.tables(corpus)
        left = annotations[annotations.evaluator == evaluator_a]
        right = annotations[annotations.evaluator == evaluator_b]
        pairs = left.merge(right, on=["corpus", "unit"], suffixes=("_a", "_b"))
        if pairs.empty:
            return {"n": 0, "kappa": None, "meets_target": False}
        import math
        kappa = float(cohen_kappa_score(pairs.label_a, pairs.label_b, labels=CLASSES))
        kappa = kappa if math.isfinite(kappa) else None
        return {"n": len(pairs), "kappa": kappa, "meets_target": kappa is not None and kappa >= .70,
                "class_order": CLASSES, "disagreement_matrix": confusion_matrix(pairs.label_a,pairs.label_b,labels=CLASSES).tolist(),
                "distribution_a": pairs.label_a.value_counts().to_dict(),
                "distribution_b": pairs.label_b.value_counts().to_dict()}

    def export(self, corpus, frame):
        annotations, decisions = self.tables(corpus)
        result = frame.drop(columns=["etiqueta", "grupo_objetivo", "justificacion"], errors="ignore").copy()
        finalized = []
        for unit in result.id_comentario:
            rows = annotations[annotations.unit == unit]
            decision = decisions[decisions.unit == unit]
            if len(rows) != 2:
                raise ValueError("Todas las unidades necesitan dos anotaciones independientes.")
            # Grupo objetivo también forma parte del acuerdo.
            if len(decision) == 1:
                row = decision.iloc[0]
                finalized.append((row.label,row.target,row.reason))
            elif rows.label.nunique() == 1 and rows.target.fillna("").nunique() == 1:
                row = rows.iloc[0]
                finalized.append((row.label,row.target,row.reason))
            else:
                raise ValueError("Hay desacuerdos pendientes de adjudicación.")
        result[["etiqueta", "grupo_objetivo", "justificacion"]] = finalized
        return result


def aiken_v(scores, lowest=1, highest=5):
    """Puntuaciones reales por criterio (filas) y especialistas (columnas)."""
    import numpy as np
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or not 3 <= scores.shape[1] <= 5 or highest <= lowest:
        raise ValueError("Se requieren entre tres y cinco jueces y una escala válida.")
    if not np.isfinite(scores).all() or (scores < lowest).any() or (scores > highest).any():
        raise ValueError("Hay valoraciones fuera de escala.")
    return ((scores-lowest).sum(axis=1)/(scores.shape[1]*(highest-lowest))).tolist()
