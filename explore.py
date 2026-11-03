import pandas as pd

chunks = pd.read_csv(
    "data/title.basics.tsv.gz",
    sep="\t",
    dtype=str,
    quoting=3,
    chunksize=500_000,
)

series = []
for chunk in chunks:
    series.append(chunk[chunk["titleType"] == "tvSeries"])

df = pd.concat(series)
print("Nombre de séries :", len(df))
print(df.head(10).to_string())
df.to_csv("data/series_basics.tsv", sep="\t", index=False)
