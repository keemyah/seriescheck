import pandas as pd

s = pd.read_csv("data/series_basics.tsv", sep="\t", dtype=str, quoting=3)
r = pd.read_csv("data/title.ratings.tsv.gz", sep="\t", dtype=str, quoting=3)

print("Lignes :", len(s))
print("\nValeurs \\N par colonne :")
print((s == "\\N").sum())
print("\nDoublons de tconst :", s["tconst"].duplicated().sum())

years = pd.to_numeric(s["startYear"], errors="coerce")
print("\nstartYear min/max :", years.min(), years.max())
rt = pd.to_numeric(s["runtimeMinutes"], errors="coerce")
print("runtimeMinutes min/max :", rt.min(), rt.max())

m = s.merge(r, on="tconst", how="left")
print("\nSéries sans note :", m["averageRating"].isna().sum())
print(m["numVotes"].astype(float).describe())
