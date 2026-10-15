"""Cálculos puros reutilizables para reportes y laboratorio de HateDetect.

Porcentajes en escala 0 a 100; tiempos en segundos. Sin acceso a bases de datos.
"""
from math import fsum, isfinite
from numbers import Integral, Real

CATEGORIES = ("Odio", "Ofensivo", "Neutro")


def validate_category(category):
    if not isinstance(category, str) or category not in CATEGORIES:
        raise ValueError("Etiqueta inválida")
    return category


def count_categories(labels):
    counts = dict.fromkeys(CATEGORIES, 0)
    for label in labels:
        counts[validate_category(label)] += 1
    return counts


def _count(value):
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError("Se requiere un conteo entero no negativo")


def hate_percentage(hate_count, total):
    _count(hate_count)
    _count(total)
    if total == 0 or hate_count > total:
        raise ValueError("Total positivo y conteo de odio no mayor que el total")
    return hate_count / total * 100


def hate_precision(true_positives, false_positives):
    _count(true_positives)
    _count(false_positives)
    total = true_positives + false_positives
    return true_positives / total * 100 if total else None


def average_latency(seconds):
    values = list(seconds)
    if any(isinstance(v, bool) or not isinstance(v, Real) or not isfinite(v) or v < 0 for v in values):
        raise ValueError("Los tiempos deben ser números finitos no negativos")
    if not values:
        return None
    return fsum(values) / len(values)
