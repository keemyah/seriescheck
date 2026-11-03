import json
import pandas as pd

MAX_YEAR = 2026
MAX_RUNTIME = 300
MIN_VOTES = 1000

journal = []

def log(operation, n, reason):
    journal.append({"operation": operation, "lignes": int(n), "raison": reason})
    print(f"{operation} : {int(n)}")

s = pd.read_csv("data/series_basics.tsv", sep="\t", dtype=str, quoting=3)
r = pd.read_csv("data/title.ratings.tsv.gz", sep="\t", dtype=str, quoting=3)
log("lignes au départ", len(s), "séries (titleType = tvSeries)")

adult = s["isAdult"] == "1"
log("lignes retirées : contenu adulte", adult.sum(), "hors sujet et titres explicites")
s = s[~adult]

n_missing = (s == "\\N").sum().sum()
s = s.replace("\\N", pd.NA)
log("valeurs \\N converties en manquant", n_missing, "vraies valeurs manquantes")

for col in ["startYear", "endYear", "runtimeMinutes"]:
    s[col] = pd.to_numeric(s[col], errors="coerce")

future = s["startYear"] > MAX_YEAR
log("lignes retirées : année de début future", future.sum(), "séries pas encore sorties")
s = s[~future]

too_long = s["runtimeMinutes"] > MAX_RUNTIME
mean_before, median_before = s["runtimeMinutes"].mean(), s["runtimeMinutes"].median()
log("durées remplacées par manquant", too_long.sum(), f"durée > {MAX_RUNTIME} min jugée aberrante")
s.loc[too_long, "runtimeMinutes"] = float("nan")
mean_after, median_after = s["runtimeMinutes"].mean(), s["runtimeMinutes"].median()
print(f"Durée moyenne : {mean_before:.1f} -> {mean_after:.1f}")
print(f"Durée médiane : {median_before:.1f} -> {median_after:.1f}")
journal.append({"operation": "effet sur la durée",
                "moyenne_avant": round(mean_before, 1), "moyenne_apres": round(mean_after, 1),
                "mediane_avant": round(median_before, 1), "mediane_apres": round(median_after, 1)})

r["averageRating"] = pd.to_numeric(r["averageRating"], errors="coerce")
r["numVotes"] = pd.to_numeric(r["numVotes"], errors="coerce")
s["statut"] = s["endYear"].apply(lambda y: "terminée" if pd.notna(y) else "en cours ou non mise à jour")
log("séries à statut incertain (endYear manquant)", (s["statut"] != "terminée").sum(),
    "IMDb Help Center : endYear omis si en cours, mais peut aussi être non mis à jour")
m = s.merge(r, on="tconst", how="left")
m["note_fiable"] = m["numVotes"] >= MIN_VOTES
log("séries avec note fiable (votes >= seuil)", m["note_fiable"].sum(), f"seuil de {MIN_VOTES} votes : décision de l'auteur, justifiée par le biais de sélection et l'incertitude en 1/racine(n)")
log("séries sans note (conservées)", m["averageRating"].isna().sum(), "pas de note dans le fichier de notes")
log("lignes à la fin", len(m), "jeu nettoyé")

m.to_csv("data/series_clean.csv", index=False)
with open("cleaning_journal.json", "w", encoding="utf-8") as f:
    json.dump(journal, f, ensure_ascii=False, indent=2)
