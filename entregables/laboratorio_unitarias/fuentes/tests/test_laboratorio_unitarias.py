"""Diez pruebas acordadas de texto, números y cálculos medibles."""
import pytest
from data_pipeline import clean_and_anonymize
from context_rules import ContextRuleBasedClassifier
from report_calculations import count_categories, hate_percentage, validate_category, hate_precision, average_latency


def evidence(record_property, case, inputs, expected, observed):
    for key, value in {"caso": case, "entrada": inputs, "esperado": expected, "observado": observed}.items():
        record_property(key, str(value))


def test_p01_normaliza_espacios(record_property):
    text = "  Hola   mundo  "
    actual = clean_and_anonymize(text)
    evidence(record_property, "PU01", repr(text), "Hola mundo", actual)
    assert actual == "Hola mundo"


def test_p02_oculta_correo(record_property):
    text = "Escribe a persona@example.com"
    actual = clean_and_anonymize(text)
    evidence(record_property, "PU02", text, "Escribe a [EMAIL]", actual)
    assert actual == "Escribe a [EMAIL]"


def test_p03_oculta_telefono(record_property):
    text = "Llámame al +51 999 123 456"
    actual = clean_and_anonymize(text)
    evidence(record_property, "PU03", text, "Llámame al [PHONE]", actual)
    assert actual == "Llámame al [PHONE]"


def test_p04_entrada_numerica(record_property):
    actual = clean_and_anonymize(12345)
    evidence(record_property, "PU04", 12345, repr(""), repr(actual))
    assert actual == ""


def test_p05_clasifica_insulto(record_property):
    text = "Eres un idiota."
    actual = ContextRuleBasedClassifier().predict_single(text)
    evidence(record_property, "PU05", text, "Ofensivo", actual)
    assert actual == "Ofensivo"


def test_p06_cuenta_categorias(record_property):
    labels = ["Odio", "Neutro", "Ofensivo", "Odio"]
    expected = {"Odio": 2, "Ofensivo": 1, "Neutro": 1}
    actual = count_categories(labels)
    evidence(record_property, "PU06", labels, expected, actual)
    assert actual == expected


def test_p07_porcentaje_odio(record_property):
    actual = hate_percentage(3, 10)
    evidence(record_property, "PU07", "Odio=3; total=10", "30 %", f"{actual:g} %")
    assert actual == pytest.approx(30, rel=0, abs=1e-9)


def test_p08_etiqueta_invalida(record_property):
    with pytest.raises(ValueError, match="^Etiqueta inválida$") as exc:
        validate_category("Violento")
    evidence(record_property, "PU08", "Violento", "ValueError: Etiqueta inválida", f"{type(exc.value).__name__}: {exc.value}")


def test_p09_precision_odio(record_property):
    actual = hate_precision(6, 2)
    evidence(record_property, "PU09", "VP=6; FP=2", "75 %", f"{actual:g} %")
    assert actual == pytest.approx(75, rel=0, abs=1e-9)


def test_p10_tiempo_promedio(record_property):
    actual = average_latency([0.20, 0.30, 0.40])
    evidence(record_property, "PU10", "0.20; 0.30; 0.40 segundos", "0.30 segundos", f"{actual:.2f} segundos")
    assert actual == pytest.approx(0.30, rel=0, abs=1e-9)
