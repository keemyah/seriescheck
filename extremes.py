import pandas as pd

s = pd.read_csv("data/series_basics.tsv", sep="\t", dtype=str, quoting=3)
s["year"] = pd.to_numeric(s["startYear"], errors="coerce")
s["end"] = pd.to_numeric(s["endYear"], errors="coerce")
s["rt"] = pd.to_numeric(s["runtimeMinutes"], errors="coerce")

print("isAdult :")
print(s["isAdult"].value_counts())

print("\nSéries avec startYear > 2026 :", (s["year"] > 2026).sum())
print(s[s["year"] > 2026][["primaryTitle", "startYear"]].head(5).to_string())

print("\nendYear avant startYear :", (s["end"] < s["year"]).sum())

print("\nLes 5 plus longues durées :")
print(s.nlargest(5, "rt")[["primaryTitle", "runtimeMinutes"]].to_string())

print("\nDurées > 300 min :", (s["rt"] > 300).sum())
