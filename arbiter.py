import re

# Un nombre : des chiffres, avec éventuellement des milliers séparés par une espace
# ("1 591", espace normale ou insécable), puis éventuellement une partie décimale
# après une virgule ou un point ("7,3").
NUMBER = re.compile(r"(?<![\w.,])(\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)(?:[.,](\d+))?")

# Nombres de contexte : le syst\u00e8me les donne lui-m\u00eame au mod\u00e8le, ils ne sont pas calcul\u00e9s.
# Chaque ajout doit avoir sa raison. Tout autre nombre doit venir d'un outil ou de la question.
CONTEXT_NUMBERS = {
    1000: "seuil MIN_VOTES de clean.py, cit\u00e9 dans la description de l'outil (note fiable)",
    10: "note maximale sur IMDb (\u00e9chelle de 1 \u00e0 10)",
}


def extract_numbers(text):
    """Renvoie la liste des nombres écrits en chiffres dans un texte, en float."""
    numbers = []
    for whole, decimals in NUMBER.findall(text or ""):
        whole = re.sub(r"\D", "", whole)
        numbers.append(float(f"{whole}.{decimals}" if decimals else whole))
    return numbers


def allowed_numbers(question, steps):
    """Les nombres autorisés : ceux de la question, ceux renvoyés par les outils, et les nombres de contexte."""
    allowed = extract_numbers(question) + [float(n) for n in CONTEXT_NUMBERS]
    for step in steps:
        for value in step["result"].values():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                allowed.append(float(value))
    return allowed


def check(answer, question, steps):
    """Accepte la réponse seulement si chacun de ses nombres a été calculé par un outil."""
    allowed = allowed_numbers(question, steps)
    unverified = [n for n in extract_numbers(answer)
                  if not any(abs(n - a) < 1e-9 for a in allowed)]
    return {"accepted": not unverified, "unverified": unverified}
