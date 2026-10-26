"""Registro local de anotación independiente y adjudicación con auditoría."""
from contextlib import closing, contextmanager
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import re
import uuid

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from data_pipeline import clean_and_anonymize

CLASSES = ["Odio", "Ofensivo", "Neutro"]
PACKAGE_SCHEMA = "hatedetect.annotation-package.v1"
PACKAGE_ROLES = {"A", "B"}
PACKAGE_TOP_LEVEL = {
    "schema", "corpus_sha256", "corpus_rows", "role", "evaluator_pseudonym",
    "exported_at", "annotations", "package_sha256",
}
PACKAGE_ANNOTATION_FIELDS = {
    "comment_id", "class", "target_group", "justification", "manual_version", "annotated_at",
}


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
            CREATE TABLE IF NOT EXISTS export_identities (
                corpus TEXT, role TEXT, evaluator TEXT, pseudonym TEXT, created TEXT,
                PRIMARY KEY(corpus, role), UNIQUE(corpus, pseudonym));
            CREATE TABLE IF NOT EXISTS package_imports (
                corpus TEXT, role TEXT, evaluator_pseudonym TEXT, package_sha256 TEXT, imported TEXT,
                PRIMARY KEY(corpus, role), UNIQUE(corpus, package_sha256));
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
        allowed_reviewers = {roles[role] for role in ("A", "B") if role in roles}
        if roles and evaluator.strip() not in allowed_reviewers:
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

    def review_completion(self, corpus, units):
        """Estado de A/B; controla cuándo puede revelarse la concordancia."""
        pair = self._reviewer_pair(corpus)
        if not pair:
            return {"complete": False, "reviewers": {}}
        progress = {role: self.progress(corpus, evaluator, units)
                    for role, evaluator in zip(("A", "B"), pair)}
        return {"complete": all(item["pending"] == 0 for item in progress.values()),
                "reviewers": progress}

    def _reviewer_pair(self, corpus):
        roles = self.reviewers(corpus)
        return (roles["A"], roles["B"]) if {"A", "B"}.issubset(roles) else None

    @staticmethod
    def _normalized_target(value):
        """Forma canónica usada en todos los controles de concordancia."""
        return " ".join(str(value or "").split()).casefold()

    def disagreements(self, corpus, evaluator_a=None, evaluator_b=None):
        pair = (evaluator_a, evaluator_b) if evaluator_a and evaluator_b else self._reviewer_pair(corpus)
        annotations, decisions = self.tables(corpus)
        if pair:
            annotations = annotations[annotations.evaluator.isin(pair)]
        paired = annotations.groupby("unit").filter(lambda rows: len(rows) == 2)
        units = []
        for unit, rows in paired.groupby("unit"):
            labels = rows.label.fillna("").astype(str).str.strip()
            targets = rows.target.map(self._normalized_target)
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
            targets = {self._normalized_target(r[2]) for r in rows}
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
            return {"n": 0, "kappa": None, "meets_target": False,
                    "stage": "pre_adjudication"}
        import math
        kappa = float(cohen_kappa_score(pairs.label_a, pairs.label_b, labels=CLASSES))
        kappa = kappa if math.isfinite(kappa) else None
        return {"n": len(pairs), "kappa": kappa, "meets_target": kappa is not None and kappa >= .70,
                "stage": "pre_adjudication",
                "class_order": CLASSES, "disagreement_matrix": confusion_matrix(pairs.label_a,pairs.label_b,labels=CLASSES).tolist(),
                "distribution_a": pairs.label_a.value_counts().to_dict(),
                "distribution_b": pairs.label_b.value_counts().to_dict()}

    @staticmethod
    def _canonical_json(value):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def package_bytes(cls, package):
        """Serializa un paquete sin depender del orden de las claves."""
        return cls._canonical_json(package)

    def export_individual(self, corpus, role, frame):
        """Exporta una revisión completa sin códigos privados ni texto del corpus."""
        role = str(role).strip().upper()
        if role not in PACKAGE_ROLES:
            raise ValueError("Solo los roles A y B pueden exportar revisiones individuales.")
        if not re.fullmatch(r"[0-9a-f]{64}", str(corpus)):
            raise ValueError("El identificador del corpus debe ser su SHA-256 en minúsculas.")
        units = frame["id_comentario"].astype(str).tolist() if "id_comentario" in frame else []
        if len(units) != 72 or len(set(units)) != 72:
            raise ValueError("El paquete requiere exactamente 72 IDs de comentario únicos.")
        roles = self.reviewers(corpus)
        evaluator = roles.get(role)
        if not evaluator:
            raise ValueError(f"El rol {role} no está registrado para este corpus.")
        annotations, _ = self.tables(corpus)
        own = annotations[annotations.evaluator == evaluator].copy()
        if len(own) != 72 or set(own.unit.astype(str)) != set(units):
            raise ValueError("La exportación exige una anotación del evaluador por cada uno de los 72 comentarios.")
        if own.unit.astype(str).duplicated().any():
            raise ValueError("La revisión contiene IDs duplicados.")
        with self.connect() as conn:
            identity = conn.execute(
                "SELECT evaluator,pseudonym FROM export_identities WHERE corpus=? AND role=?",
                (corpus, role),
            ).fetchone()
            if identity:
                if identity[0] != evaluator:
                    raise ValueError("La identidad de exportación no corresponde al evaluador registrado.")
                pseudonym = identity[1]
            else:
                pseudonym = f"reviewer-{uuid.uuid4()}"
                conn.execute(
                    "INSERT INTO export_identities VALUES (?,?,?,?,?)",
                    (corpus, role, evaluator, pseudonym, datetime.now(timezone.utc).isoformat()),
                )
        indexed = own.assign(unit=own.unit.astype(str)).set_index("unit")
        records = []
        for unit in units:
            item = indexed.loc[unit]
            records.append({
                "comment_id": unit,
                "class": item.label,
                "target_group": item.target,
                "justification": item.reason,
                "manual_version": item.manual_version,
                "annotated_at": item.created,
            })
        body = {
            "schema": PACKAGE_SCHEMA,
            "corpus_sha256": corpus,
            "corpus_rows": 72,
            "role": role,
            "evaluator_pseudonym": pseudonym,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "annotations": records,
        }
        body["package_sha256"] = hashlib.sha256(self._canonical_json(body)).hexdigest()
        return body

    @classmethod
    def _validated_package(cls, package, corpus_hash, expected_units):
        if isinstance(package, (bytes, bytearray, str)):
            try:
                package = json.loads(package)
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
                raise ValueError("El paquete no contiene JSON válido.") from exc
        if not isinstance(package, dict) or set(package) != PACKAGE_TOP_LEVEL:
            raise ValueError("El paquete tiene una estructura no permitida.")
        string_fields = {
            "schema": package["schema"],
            "corpus_sha256": package["corpus_sha256"],
            "role": package["role"],
            "evaluator_pseudonym": package["evaluator_pseudonym"],
            "exported_at": package["exported_at"],
            "package_sha256": package["package_sha256"],
        }
        if any(type(value) is not str or not value.strip() for value in string_fields.values()):
            raise ValueError("Los identificadores, hashes y fechas del paquete deben ser cadenas no vacías.")
        if type(package["corpus_rows"]) is not int:
            raise ValueError("La cantidad de filas del paquete debe ser un número entero.")
        if not isinstance(package["annotations"], list):
            raise ValueError("La colección de anotaciones debe ser una lista.")
        supplied_digest = package["package_sha256"]
        if not re.fullmatch(r"[0-9a-f]{64}", supplied_digest):
            raise ValueError("El hash de integridad del paquete no es válido.")
        body = {key: value for key, value in package.items() if key != "package_sha256"}
        actual_digest = hashlib.sha256(cls._canonical_json(body)).hexdigest()
        if not hmac.compare_digest(supplied_digest, actual_digest):
            raise ValueError("El paquete está corrupto o fue modificado.")
        if package["schema"] != PACKAGE_SCHEMA:
            raise ValueError("La versión del paquete no es compatible.")
        if not re.fullmatch(r"[0-9a-f]{64}", package["corpus_sha256"]):
            raise ValueError("El hash del corpus no tiene un formato SHA-256 válido.")
        if package["corpus_sha256"] != corpus_hash:
            raise ValueError("El hash del corpus no coincide.")
        if package["corpus_rows"] != 72 or len(expected_units) != 72:
            raise ValueError("El corpus y el paquete deben contener exactamente 72 comentarios.")
        role = package["role"]
        if role not in PACKAGE_ROLES:
            raise ValueError("El paquete declara un rol incorrecto; solo se aceptan A y B.")
        pseudonym = package["evaluator_pseudonym"]
        try:
            if not str(pseudonym).startswith("reviewer-"):
                raise ValueError
            uuid.UUID(str(pseudonym).removeprefix("reviewer-"))
        except (ValueError, AttributeError) as exc:
            raise ValueError("El identificador seudónimo no es válido.") from exc
        try:
            exported = datetime.fromisoformat(package["exported_at"])
        except ValueError as exc:
            raise ValueError("La fecha de exportación no es válida.") from exc
        if exported.tzinfo is None:
            raise ValueError("La fecha de exportación debe incluir zona horaria.")
        records = package["annotations"]
        if not isinstance(records, list) or len(records) != 72:
            raise ValueError("El paquete debe contener exactamente 72 anotaciones.")
        seen = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != PACKAGE_ANNOTATION_FIELDS:
                raise ValueError("Una anotación tiene campos faltantes o no permitidos.")
            if type(record["comment_id"]) is not str or not record["comment_id"].strip():
                raise ValueError("El ID del comentario debe ser una cadena no vacía.")
            if type(record["class"]) is not str:
                raise ValueError("La clase debe ser una cadena de texto válida.")
            if type(record["target_group"]) is not str:
                raise ValueError("El grupo objetivo debe ser una cadena de texto.")
            if type(record["justification"]) is not str or not record["justification"].strip():
                raise ValueError("La justificación debe ser una cadena no vacía.")
            if type(record["manual_version"]) is not str or not record["manual_version"].strip():
                raise ValueError("La versión del manual debe ser una cadena no vacía.")
            if type(record["annotated_at"]) is not str or not record["annotated_at"].strip():
                raise ValueError("La fecha de anotación debe ser una cadena no vacía.")
            unit = record["comment_id"]
            if unit in seen:
                raise ValueError("El paquete contiene registros duplicados.")
            seen.add(unit)
            cls.validate(record["class"], record["target_group"], record["justification"])
            try:
                annotated = datetime.fromisoformat(record["annotated_at"])
            except ValueError as exc:
                raise ValueError("Una fecha de anotación no es válida.") from exc
            if annotated.tzinfo is None:
                raise ValueError("Las fechas de anotación deben incluir zona horaria.")
        if seen != set(expected_units):
            raise ValueError("Los IDs del paquete no coinciden con el CSV de 72 comentarios.")
        return package

    @classmethod
    def consolidate_packages(cls, destination, packages, corpus_content, frame):
        """Valida A+B y crea una base central nueva; nunca sobrescribe destinos."""
        destination = Path(destination)
        if destination.exists():
            raise FileExistsError("La base central de destino ya existe; no se sobrescribe.")
        corpus_hash = hashlib.sha256(corpus_content).hexdigest()
        units = frame["id_comentario"].astype(str).tolist() if "id_comentario" in frame else []
        if len(units) != 72 or len(set(units)) != 72:
            raise ValueError("El CSV central debe contener exactamente 72 IDs únicos.")
        validated = [cls._validated_package(item, corpus_hash, units) for item in packages]
        if len(validated) != 2 or {item["role"] for item in validated} != PACKAGE_ROLES:
            raise ValueError("Se requiere exactamente un paquete del rol A y uno del rol B.")
        if len({item["evaluator_pseudonym"] for item in validated}) != 2:
            raise ValueError("Cada rol debe pertenecer a un evaluador seudónimo distinto.")
        if len({item["package_sha256"] for item in validated}) != 2:
            raise ValueError("No se puede importar dos veces el mismo paquete.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(descriptor)
        except FileExistsError as exc:
            raise FileExistsError("La base central de destino ya existe; no se sobrescribe.") from exc
        try:
            store = cls(destination)
            with store.connect() as conn:
                now = datetime.now(timezone.utc).isoformat()
                for package in validated:
                    role, pseudonym = package["role"], package["evaluator_pseudonym"]
                    conn.execute(
                        "INSERT INTO reviewer_roles VALUES (?,?,?,?)", (corpus_hash, role, pseudonym, now)
                    )
                    conn.execute(
                        "INSERT INTO package_imports VALUES (?,?,?,?,?)",
                        (corpus_hash, role, pseudonym, package["package_sha256"], now),
                    )
                    conn.executemany(
                        "INSERT INTO annotations VALUES (?,?,?,?,?,?,?,?)",
                        [(corpus_hash, item["comment_id"], pseudonym, item["class"],
                          clean_and_anonymize(item["target_group"]), clean_and_anonymize(item["justification"]),
                          item["manual_version"], item["annotated_at"])
                         for item in package["annotations"]],
                    )
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return store

    def export(self, corpus, frame):
        annotations, decisions = self.tables(corpus)
        roles = self.reviewers(corpus)
        with self.connect() as conn:
            imported = conn.execute(
                "SELECT count(*) FROM package_imports WHERE corpus=?", (corpus,)
            ).fetchone()[0]
        if imported and "E3" not in roles:
            raise ValueError("La base consolidada requiere registrar al adjudicador E3 antes del CSV final.")
        if roles and not {"A", "B"}.issubset(roles):
            raise ValueError("La exportación requiere registrar los roles A y B.")
        pair = (roles["A"], roles["B"]) if roles else None
        if pair is not None:
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
            elif (rows.label.nunique() == 1 and
                  rows.target.map(self._normalized_target).nunique() == 1):
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
