import pandas as pd

OPERATIONS = ["count", "median", "max", "percent"]
COLUMNS = ["startYear", "endYear", "runtimeMinutes", "averageRating", "numVotes"]


def load_series(path="data/series_clean.csv"):
    return pd.read_csv(path)


def compute(df, operation, column=None, year=None, genre=None, reliable_only=False):
    if operation not in OPERATIONS:
        return {"error": f"operation inconnue : {operation}. Valeurs permises : {OPERATIONS}"}
    if operation != "count" and column not in COLUMNS:
        return {"error": f"colonne inconnue : {column}. Valeurs permises : {COLUMNS}"}

    d = df
    if year is not None:
        try:
            year = int(year)
        except (TypeError, ValueError):
            return {"error": f"annee invalide : {year}"}
        d = d[d["startYear"] == year]
    if genre is not None:
        has_genre = d["genres"].fillna("").str.split(",").apply(lambda g: genre in g)
        d = d[has_genre.astype(bool)]
    if reliable_only:
        d = d[d["note_fiable"]]

    if operation == "count":
        return {"result": len(d), "rows_used": len(d)}
    if operation == "percent":
        if len(d) == 0:
            return {"error": "aucune ligne ne correspond aux filtres"}
        n = int(d[column].notna().sum())
        return {"result": round(100 * n / len(d), 1), "rows_used": len(d)}

    values = d[column].dropna()
    if len(values) == 0:
        return {"error": "aucune valeur disponible pour ce calcul"}
    value = values.median() if operation == "median" else values.max()
    return {"result": float(value), "rows_used": len(values)}
