"""Brique 9 : ton système (Qwen + outil + arbitre) face à Qwen seul.

10 questions à réponse connue, plusieurs lancements par candidat.
Usage : python benchmark.py [nombre_de_lancements]   (3 par défaut)
        python benchmark.py --rescore                 (re-note results/runs.json sans relancer Qwen)
"""
import json
import statistics
import sys
import time
from pathlib import Path

from agent import MODEL, ask, call_ollama
from arbiter import extract_numbers
from expected import QUESTIONS, expected_answers
from tools import load_series

RESULTS_DIR = Path("results")
ALONE_PROMPT = "Réponds à la question par un nombre, en une phrase."


def grade(final, expected, refused=False, question=""):
    """Verdict d'une réponse : juste, faux, ou refusé (arbitre ou aucun nombre).

    Les nombres déjà présents dans la question (comme l'année 2015) ne comptent pas
    comme une réponse : « je ne connais pas les séries de 2015 » est un refus, pas un faux.
    """
    if refused:
        return "refusé"
    in_question = extract_numbers(question)
    numbers = [n for n in extract_numbers(final)
               if not any(abs(n - q) < 1e-9 for q in in_question)]
    if not numbers:
        return "refusé"
    if any(abs(n - expected) < 1e-9 for n in numbers):
        return "juste"
    return "faux"


def run_system(question, df):
    trace = ask(question, df)
    refused = trace["answer"] is None or not trace["verdict"]["accepted"]
    return trace["final"], refused, trace


def run_alone(question, df=None, chat=call_ollama):
    start = time.time()
    messages = [{"role": "system", "content": ALONE_PROMPT},
                {"role": "user", "content": question}]
    answer = chat(messages, tools=()).get("content", "")
    trace = {"question": question, "model": MODEL, "answer": answer,
             "seconds": round(time.time() - start, 1)}
    return answer, False, trace


CANDIDATES = {"systeme": run_system, "qwen_seul": run_alone}


def summarize(rows, n_tasks):
    summary = {}
    for name in CANDIDATES:
        mine = [r for r in rows if r["candidate"] == name]
        runs = sorted({r["run"] for r in mine})
        scores = [sum(r["verdict"] == "juste" for r in mine if r["run"] == run) for run in runs]
        summary[name] = {
            "justes_par_lancement": scores,
            "moyenne": round(statistics.mean(scores), 2),
            "ecart_type": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
            "sur": n_tasks,
            "total_justes": sum(r["verdict"] == "juste" for r in mine),
            "total_faux": sum(r["verdict"] == "faux" for r in mine),
            "total_refuses": sum(r["verdict"] == "refusé" for r in mine),
            "total_reponses": len(mine),
        }
    return summary


def main(n_runs=3):
    df = load_series()
    expected = expected_answers(df)
    RESULTS_DIR.mkdir(exist_ok=True)
    rows = []
    for run in range(1, n_runs + 1):
        for name, candidate in CANDIDATES.items():
            for task, question in QUESTIONS.items():
                final, refused, trace = candidate(question, df)
                verdict = grade(final, expected[task], refused, question)
                rows.append({"run": run, "candidate": name, "task": task, "question": question,
                             "expected": expected[task], "final": final, "verdict": verdict,
                             "trace": trace})
                print(f"lancement {run} | {name:<9} | tâche {task:>2} | {verdict:<6} | {final}")
                # Écrit après chaque réponse : rien n'est perdu si le benchmark s'arrête en route.
                (RESULTS_DIR / "runs.json").write_text(
                    json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = summarize(rows, len(QUESTIONS))
    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def rescore():
    """Re-note les réponses déjà enregistrées, sans rappeler Qwen (après un changement de notation)."""
    rows = json.loads((RESULTS_DIR / "runs.json").read_text(encoding="utf-8"))
    for r in rows:
        refused = r["final"].startswith("Réponse refusée") if r["candidate"] == "systeme" else False
        r["verdict"] = grade(r["final"], r["expected"], refused, r["question"])
    (RESULTS_DIR / "runs.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = summarize(rows, len(QUESTIONS))
    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rescore":
        rescore()
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
