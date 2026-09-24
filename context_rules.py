"""Reglas v2 acotadas: no equivalen a comprensión semántica ni modelo validado.

La clase histórica se conserva para que sus artefactos sigan reproduciéndose.
"""
import re
import unicodedata

from model_classes import RuleBasedClassifier


class ContextRuleBasedClassifier(RuleBasedClassifier):
    VERSION = "2.0"
    GROUP = (
        r"(?:catolic[oa]s?|cristian[oa]s?|judi[oa]s?|musulman(?:es)?|"
        r"refugiad[oa]s?|inmigrantes?|extranjer[oa]s?|gitan[oa]s?|"
        r"homosexuales?|personas trans|mujeres|hombres|"
        r"catholics?|christians?|jews?|muslims?|refugees?|immigrants?|"
        r"foreigners?|gay people|trans people|women|men)"
    )
    EXCLUSION = (
        r"(?:no (?:deben|deberian|pueden|merecen) (?:opinar|votar|entrar|vivir|estar aqui|tener derechos)|"
        r"(?:should|must) not (?:speak|vote|live here|have rights)|"
        r"(?:shouldn't|mustn't) (?:speak|vote|live here|have rights)|"
        r"(?:do not|don't) deserve rights)"
    )
    DEHUMANIZATION = r"(?:basura|escoria|plaga|parasitos?|subhumanos?|vermin|scum|parasites?|subhumans?)"
    VIOLENCE = r"(?:matar|exterminar|expulsar|eliminar|kill|exterminate|expel|deport)"
    DENIAL = re.compile(
        r"\b(?:no es (?:cierto|verdad) que|es falso que|rechazo que|"
        r"it is not true that|it is false that|i reject that|no)\s*$"
    )
    QUOTE = re.compile(r'"[^"\n]+"|“[^”\n]+”|«[^»\n]+»')
    CONDEMN = re.compile(
        r"\b(?:rechazo|condeno|denuncio|es discriminatorio|es inaceptable|"
        r"i condemn|i reject|is discriminatory|is unacceptable)\b"
    )

    def __init__(self):
        # No heredar la detección de odio por mera mención identitaria.
        self.offensive_regex = re.compile("|".join(self.OFFENSIVE_PATTERNS), re.IGNORECASE)
        group = rf"\b{self.GROUP}\b"
        gap = r"(?:\s+\w+){0,6}\s+"
        self.attack_patterns = [
            re.compile(group + gap + self.EXCLUSION),
            re.compile(group + r"\s+(?:son|es|are|is)\s+(?:(?:una?|unos?|unas|a|an)\s+)?" + self.DEHUMANIZATION + r"\b"),
            re.compile(r"\b(?:hay que|debemos|deben|quiero|we must|we should|let's)\s+" + self.VIOLENCE + gap + group),
            re.compile(r"^\s*" + self.VIOLENCE + gap + group),
        ]

    @staticmethod
    def normalize(text):
        return "".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                       if not unicodedata.combining(c)).replace("’", "'")

    def predict_single(self, text):
        if not isinstance(text, str):
            return "Neutro"
        text = self.normalize(text)
        offensive = False
        # Acotar cada decisión a una oración o cláusula de contraste.
        for clause in re.split(r"[.!?;\n]+|\b(?:pero|but|sin embargo|however)\b", text):
            outside_quotes = self.QUOTE.sub("", clause)
            condemnation = any(
                not re.search(r"\b(?:no|not|don't|do not)\s*$", outside_quotes[:m.start()])
                for m in self.CONDEMN.finditer(outside_quotes)
            )
            if condemnation:
                clause = outside_quotes
            for pattern in self.attack_patterns:
                for match in pattern.finditer(clause):
                    prefix = clause[:match.start()]
                    prefix = re.sub(r"\b(?:los|las|the)\s+$", "", prefix)
                    if not self.DENIAL.search(prefix):
                        return "Odio"
            # Evitar insultos explícitamente negados, sin borrar ataques posteriores.
            for match in self.offensive_regex.finditer(clause):
                prefix = clause[:match.start()]
                if not re.search(r"\b(?:no eres|no es|no son|not|isn't|aren't)\s+(?:(?:un|una|a|an)\s+)?$", prefix):
                    offensive = True
        return "Ofensivo" if offensive else "Neutro"
