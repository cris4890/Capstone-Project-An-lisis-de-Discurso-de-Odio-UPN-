import joblib
import pytest

from context_rules import ContextRuleBasedClassifier
from model_classes import RuleBasedClassifier


@pytest.mark.parametrize("text,expected", [
    ("las personas de religion catolica no deben opinar", "Odio"),
    ("Las personas de religión católica no deben opinar.", "Odio"),
    ("Los refugiados merecen respeto", "Neutro"),
    ("Los judíos celebran una fiesta", "Neutro"),
    ("Muslim refugees deserve respect", "Neutro"),
    ("Las personas católicas pueden opinar", "Neutro"),
    ("Los inmigrantes son una plaga", "Odio"),
    ("Immigrants are parasites", "Odio"),
    ("Catholics should not vote", "Odio"),
    ("Catholics shouldn't vote", "Odio"),
    ("Hay que expulsar a los musulmanes", "Odio"),
    ("We must kill all immigrants", "Odio"),
    ("No hay que expulsar a los musulmanes", "Neutro"),
    ("No es cierto que los inmigrantes son una plaga", "Neutro"),
    ("It is not true that immigrants are parasites", "Neutro"),
    ('Condeno la frase "los inmigrantes son una plaga"', "Neutro"),
    ('"Immigrants are parasites" is discriminatory', "Neutro"),
    ('No condeno "los inmigrantes son una plaga"', "Odio"),
    ('Condeno el racismo. Los católicos no deben votar', "Odio"),
    ('No es cierto que los inmigrantes son una plaga, pero los católicos no deben votar', "Odio"),
    ('Condeno "los inmigrantes son una plaga", pero los católicos no deben votar', "Odio"),
    ("Los refugiados merecen respeto. Los católicos no deben votar", "Odio"),
    ("Los refugiados merecen respeto. Eres un idiota", "Ofensivo"),
    ("No eres un idiota", "Neutro"),
    ("No eres un idiota, pero eres un imbécil", "Ofensivo"),
    ("Eres un idiota", "Ofensivo"),
    ("You are an idiot", "Ofensivo"),
    ("Gracias por compartir la información", "Neutro"),
    ("Thank you for your help", "Neutro"),
])
def test_context_regressions(text, expected):
    assert ContextRuleBasedClassifier().predict_single(text) == expected


def test_legacy_and_v2_artifacts_remain_distinct(tmp_path):
    text = ["Los refugiados merecen respeto"]
    old = RuleBasedClassifier()
    new = ContextRuleBasedClassifier()
    for name, model, expected in [("old", old, "Odio"), ("new", new, "Neutro")]:
        path = tmp_path / (name + ".pkl")
        joblib.dump(model, path)
        assert joblib.load(path).predict(text).tolist() == [expected]
