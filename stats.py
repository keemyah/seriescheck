"""Brique 8 : intervalles de confiance sur les résultats du benchmark.

Usage : python stats.py   (lit results/runs.json, écrit results/intervals.json)
"""
import json
import math
from pathlib import Path

RESULTS_DIR = Path("results")
Z = 1.96  # niveau de confiance de 95 %


def wilson(k, n, z=Z):
    """Intervalle de Wilson pour une proportion k/n : (bas, haut), toujours entre 0 et 1.

    Contrairement à p ± z * racine(p(1-p)/n) (Wald), il ne dépasse jamais 100 %
    et ne se réduit pas à un seul point quand k = 0 ou k = n.
    """
    if n == 0:
        raise ValueError("n doit être supérieur à 0")
    p = k / n
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def describe(k, n):
    low, high = wilson(k, n)
    return {"k": k, "n": n, "proportion": round(k / n, 3),
            "ic95_bas": round(low, 3), "ic95_haut": round(high, 3)}


def per_answer(rows, candidate, verdict):
    """Toutes les réponses comptent : 10 questions x 3 lancements = 30."""
    mine = [r for r in rows if r["candidate"] == candidate]
    return describe(sum(r["verdict"] == verdict for r in mine), len(mine))


def per_question(rows, candidate, verdict):
    """Version prudente : une question compte si le verdict sort dans la majorité de ses lancements."""
    mine = [r for r in rows if r["candidate"] == candidate]
    tasks = sorted({r["task"] for r in mine})
    k = 0
    for task in tasks:
        verdicts = [r["verdict"] for r in mine if r["task"] == task]
        if verdicts.count(verdict) > len(verdicts) / 2:
            k += 1
    return describe(k, len(tasks))


def main():
    rows = json.loads((RESULTS_DIR / "runs.json").read_text(encoding="utf-8"))
    intervals = {}
    for candidate in ["systeme", "qwen_seul"]:
        intervals[candidate] = {
            "justes_sur_30_reponses": per_answer(rows, candidate, "juste"),
            "faux_sur_30_reponses": per_answer(rows, candidate, "faux"),
            "justes_sur_10_questions": per_question(rows, candidate, "juste"),
            "faux_sur_10_questions": per_question(rows, candidate, "faux"),
        }
    (RESULTS_DIR / "intervals.json").write_text(
        json.dumps(intervals, ensure_ascii=False, indent=2), encoding="utf-8")
    for candidate, measures in intervals.items():
        for name, m in measures.items():
            print(f"{candidate:<9} | {name:<24} | {m['k']:>2}/{m['n']:<2} = {100 * m['proportion']:5.1f} % "
                  f"| IC 95 % : {100 * m['ic95_bas']:5.1f} % à {100 * m['ic95_haut']:5.1f} %")


if __name__ == "__main__":
    main()
