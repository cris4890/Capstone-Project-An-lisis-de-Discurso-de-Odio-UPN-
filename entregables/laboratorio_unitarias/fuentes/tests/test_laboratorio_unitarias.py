"""Diez casos unitarios identificables para el laboratorio académico.

Las propiedades conservan entradas y salidas reales en el reporte JUnit XML.
"""
import pytest

from data_pipeline import clean_and_anonymize
from experiment import metrics_for, select_model


def evidence(record_property, case, inputs, expected, observed):
    for key, value in {"caso": case, "entrada": inputs, "esperado": expected,
                       "observado": observed}.items():
        record_property(key, str(value))


def test_p01_normaliza_espacios(record_property):
    actual = clean_and_anonymize("  Hola\n  mundo  ")
    evidence(record_property, "P01", r"  Hola\n  mundo  ", "Hola mundo", actual)
    assert actual == "Hola mundo"


def test_p02_oculta_correo(record_property):
    actual = clean_and_anonymize("Escribe a persona@example.com")
    evidence(record_property, "P02", "Escribe a persona@example.com", "Escribe a [EMAIL]", actual)
    assert actual == "Escribe a [EMAIL]"


def test_p03_conserva_negacion_y_tildes(record_property):
    text = "No odio a nadie. Qué alegría."
    actual = clean_and_anonymize(text)
    evidence(record_property, "P03", text, text, actual)
    assert actual == text


def test_p04_entrada_nula(record_property):
    actual = clean_and_anonymize(None)
    evidence(record_property, "P04", "None", repr(""), repr(actual))
    assert actual == ""


def test_p05_texto_vacio(record_property):
    actual = clean_and_anonymize("")
    evidence(record_property, "P05", repr(""), repr(""), repr(actual))
    assert actual == ""


def test_p06_elige_mayor_validacion(record_property):
    scores = {"modelo_a": 0.80, "modelo_b": 0.30}
    actual = select_model(scores)
    evidence(record_property, "P06", scores, "modelo_a", actual)
    assert actual == "modelo_a"


def test_p07_rechaza_validacion_vacia(record_property):
    with pytest.raises(ValueError, match="Puntuaciones de validación inválidas") as exc:
        select_model({})
    evidence(record_property, "P07", "{}", "ValueError", type(exc.value).__name__)


def test_p08_rechaza_nan(record_property):
    with pytest.raises(ValueError, match="Puntuaciones de validación inválidas") as exc:
        select_model({"modelo_a": float("nan")})
    evidence(record_property, "P08", "modelo_a: NaN", "ValueError", type(exc.value).__name__)


def test_p09_tasa_falsos_negativos(record_property):
    actual = metrics_for(["Odio", "Odio", "Neutro"], ["Odio", "Neutro", "Odio"])["per_class"]["Odio"]["fnr"]
    evidence(record_property, "P09", "Real: Odio,Odio,Neutro; predicho: Odio,Neutro,Odio", 0.5, actual)
    assert actual == pytest.approx(0.5, abs=1e-9)


def test_p10_clase_sin_soporte(record_property):
    actual = metrics_for(["Neutro"], ["Neutro"])["per_class"]["Odio"]["fnr"]
    evidence(record_property, "P10", "Real: Neutro; predicho: Neutro; FNR de Odio", "None", actual)
    assert actual is None
