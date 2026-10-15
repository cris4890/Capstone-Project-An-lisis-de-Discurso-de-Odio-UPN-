"""Límites adicionales, separados de los diez casos del laboratorio."""
import pytest
from report_calculations import (
    count_categories, validate_category, hate_percentage, hate_precision, average_latency,
)


def test_empty_and_undefined_results():
    assert count_categories([]) == {"Odio": 0, "Ofensivo": 0, "Neutro": 0}
    assert hate_precision(0, 0) is None
    assert average_latency([]) is None
    assert average_latency([0, 0]) == 0
    assert hate_percentage(0, 5) == 0
    assert hate_percentage(5, 5) == 100
    assert hate_precision(0, 5) == 0
    assert hate_precision(5, 0) == 100


@pytest.mark.parametrize("label", [None, 3, "", "odio", ["Odio"]])
def test_invalid_category(label):
    with pytest.raises(ValueError):
        validate_category(label)
    with pytest.raises(ValueError):
        count_categories([label])


@pytest.mark.parametrize("bad", [-1, 1.5, True, "3", float("nan")])
def test_invalid_counts(bad):
    with pytest.raises(ValueError):
        hate_percentage(bad, 10)
    with pytest.raises(ValueError):
        hate_percentage(1, bad)
    with pytest.raises(ValueError):
        hate_precision(bad, 2)
    with pytest.raises(ValueError):
        hate_precision(2, bad)


@pytest.mark.parametrize("counts", [(0, 0), (3, 2)])
def test_impossible_percentage(counts):
    with pytest.raises(ValueError):
        hate_percentage(*counts)


@pytest.mark.parametrize("bad", [-.1, float("nan"), float("inf"), True, "0.3"])
def test_invalid_latency(bad):
    with pytest.raises(ValueError):
        average_latency([.2, bad])


def test_valid_labels():
    for label in ("Odio", "Ofensivo", "Neutro"):
        assert validate_category(label) == label
