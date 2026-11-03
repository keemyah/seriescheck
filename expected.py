"""Réponses attendues du benchmark, calculées sans passer par tools.py.

Les filtres sont écrits autrement que dans compute() (expression régulière pour le genre,
seuil de votes recalculé au lieu de la colonne note_fiable) : si les deux calculs
tombent d'accord, une erreur commune aux deux est peu probable.
"""
import pandas as pd

MIN_VOTES = 1000

QUESTIONS = {
    1: "Combien de séries ont commencé en 2015 ?",
    2: "Combien de séries Drama ont commencé en 2015 ?",
    3: "Quelle est la note médiane des séries à note fiable ?",
    4: "Quelle est la note maximale des séries à note fiable ?",
    5: "Quelle part des séries a une date de fin renseignée ?",
    6: "Combien de séries Comedy sont à note fiable ?",
    7: "Combien de séries ont commencé en 2020 ?",
    8: "Combien de séries Crime sont à note fiable ?",
    9: "Quel est le nombre médian de votes des séries à note fiable ?",
    10: "Quelle part des séries commencées en 2010 a une date de fin ?",
}


def has_genre(df, genre):
    # Le genre doit être un élément entier de la liste "Drama,Crime", pas un morceau de mot.
    return df["genres"].fillna("").str.contains(rf"(?:^|,){genre}(?:,|$)", regex=True)


def expected_answers(df):
    reliable = df["numVotes"] >= MIN_VOTES
    started_2010 = df[df["startYear"] == 2010]
    return {
        1: int((df["startYear"] == 2015).sum()),
        2: int((has_genre(df, "Drama") & (df["startYear"] == 2015)).sum()),
        3: float(df.loc[reliable, "averageRating"].median()),
        4: float(df.loc[reliable, "averageRating"].max()),
        5: round(100 * df["endYear"].notna().mean(), 1),
        6: int((has_genre(df, "Comedy") & reliable).sum()),
        7: int((df["startYear"] == 2020).sum()),
        8: int((has_genre(df, "Crime") & reliable).sum()),
        9: float(df.loc[reliable, "numVotes"].median()),
        10: round(100 * started_2010["endYear"].notna().mean(), 1),
    }


if __name__ == "__main__":
    # Comparaison avec l'outil : les deux colonnes doivent être identiques.
    from tools import compute, load_series

    df = load_series()
    by_tool = {
        1: compute(df, "count", year=2015),
        2: compute(df, "count", genre="Drama", year=2015),
        3: compute(df, "median", column="averageRating", reliable_only=True),
        4: compute(df, "max", column="averageRating", reliable_only=True),
        5: compute(df, "percent", column="endYear"),
        6: compute(df, "count", genre="Comedy", reliable_only=True),
        7: compute(df, "count", year=2020),
        8: compute(df, "count", genre="Crime", reliable_only=True),
        9: compute(df, "median", column="numVotes", reliable_only=True),
        10: compute(df, "percent", column="endYear", year=2010),
    }
    for task, value in expected_answers(df).items():
        tool_value = by_tool[task]["result"]
        status = "OK" if abs(value - tool_value) < 1e-9 else "DIFFÉRENT"
        print(f"{task:>2}. attendu {value} | outil {tool_value} | {status} | {QUESTIONS[task]}")
