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
            CREATE TABLE IF NOT EXISTS reviewer_roles (
                corpus TEXT, role TEXT, evaluator TEXT, created TEXT,
                PRIMARY KEY(corpus, role), UNIQUE(corpus, evaluator));
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
        roles = self.reviewers(corpus)
        if {"A", "B"}.issubset(roles) and evaluator.strip() not in {roles["A"], roles["B"]}:
            raise ValueError("Solo los códigos vinculados a los roles A y B pueden anotar.")
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

    def claim_role(self, corpus, role, evaluator):
        """Vincula de forma inmutable un código local con A, B o E3."""
        role, evaluator = str(role).strip().upper(), str(evaluator).strip()
        if not str(corpus).strip() or role not in {"A", "B", "E3"} or not evaluator:
            raise ValueError("Indique un corpus, rol A/B/E3 y código de evaluador.")
        with self.connect() as conn:
            current = conn.execute(
                "SELECT evaluator FROM reviewer_roles WHERE corpus=? AND role=?", (corpus, role)
            ).fetchone()
            if current:
                if current[0] != evaluator:
                    raise ValueError("El rol ya está vinculado a otro código para este corpus.")
                return
            try:
                conn.execute(
                    "INSERT INTO reviewer_roles VALUES (?,?,?,?)",
                    (corpus, role, evaluator, datetime.now(timezone.utc).isoformat()),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("El código ya está vinculado a otro rol para este corpus.") from exc

    def reviewers(self, corpus):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT role,evaluator FROM reviewer_roles WHERE corpus=? ORDER BY role", (corpus,)
            ).fetchall()
        return dict(rows)

    def progress(self, corpus, evaluator, units):
        units = [str(unit) for unit in units]
        annotations, _ = self.tables(corpus)
        completed = set(annotations.loc[annotations.evaluator == str(evaluator).strip(), "unit"])
        done = sum(unit in completed for unit in units)
        return {"total": len(units), "completed": done, "pending": len(units) - done,
                "fraction": done / len(units) if units else 0.0}

    def _reviewer_pair(self, corpus):
        roles = self.reviewers(corpus)
        return (roles["A"], roles["B"]) if {"A", "B"}.issubset(roles) else None

    def disagreements(self, corpus, evaluator_a=None, evaluator_b=None):
        pair = (evaluator_a, evaluator_b) if evaluator_a and evaluator_b else self._reviewer_pair(corpus)
        annotations, decisions = self.tables(corpus)
        if pair:
            annotations = annotations[annotations.evaluator.isin(pair)]
        paired = annotations.groupby("unit").filter(lambda rows: len(rows) == 2)
        units = []
        for unit, rows in paired.groupby("unit"):
            labels = rows.label.fillna("").astype(str).str.strip()
            targets = rows.target.fillna("").astype(str).str.strip().str.casefold()
            if labels.nunique() > 1 or targets.nunique() > 1:
                units.append(unit)
        decided = set(decisions.unit)
        return {"all": sorted(units), "pending": sorted(set(units) - decided),
                "resolved": sorted(set(units) & decided)}

    @staticmethod
    def validate(label, target, reason):
        if label not in CLASSES or not str(reason).strip():
            raise ValueError("Seleccione una clase y justifique la decisión.")
        if label == "Odio" and not str(target).strip():
            raise ValueError("Registre el grupo o atributo objetivo del ataque.")

    def adjudicate(self, corpus, unit, evaluator, label, target, reason):
        self.validate(label,target,reason)
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT evaluator,label,target FROM annotations WHERE corpus=? AND unit=?", (corpus,unit)
            ).fetchall()
            roles = self.reviewers(corpus)
            expected_pair = {roles["A"], roles["B"]} if {"A", "B"}.issubset(roles) else None
            actual_pair = {r[0] for r in rows}
            if len(rows) != 2 or not evaluator.strip() or evaluator.strip() in actual_pair:
                raise ValueError("La adjudicación requiere dos anotaciones y un tercer evaluador.")
            if expected_pair and actual_pair != expected_pair:
                raise ValueError("La adjudicación requiere las anotaciones de los roles A y B.")
            if roles.get("E3") and evaluator.strip() != roles["E3"]:
                raise ValueError("La decisión debe registrarla el código vinculado al rol E3.")
            labels = {r[1] for r in rows}
            targets = {str(r[2] or "").strip().casefold() for r in rows}
            if len(labels) == 1 and len(targets) == 1:
                raise ValueError("Solo los desacuerdos pueden adjudicarse.")
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
                "stage": "pre_adjudication",
                "class_order": CLASSES, "disagreement_matrix": confusion_matrix(pairs.label_a,pairs.label_b,labels=CLASSES).tolist(),
                "distribution_a": pairs.label_a.value_counts().to_dict(),
                "distribution_b": pairs.label_b.value_counts().to_dict()}

    def export(self, corpus, frame):
        annotations, decisions = self.tables(corpus)
        pair = self._reviewer_pair(corpus)
        if pair:
            annotations = annotations[annotations.evaluator.isin(pair)]
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
