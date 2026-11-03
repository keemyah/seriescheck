import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from tools import compute, load_series

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen35-4b-8k"
MAX_TURNS = 5
TRACES_DIR = Path("traces")

SYSTEM_PROMPT = (
    "Tu réponds à des questions chiffrées sur des séries TV (données IMDb). "
    "Tu ne calcules jamais toi-même : tu appelles l'outil compute, "
    "puis tu donnes le chiffre renvoyé par l'outil, sans en inventer d'autre. "
    "Réponds en français, en une ou deux phrases."
)

TOOL = {
    "type": "function",
    "function": {
        "name": "compute",
        "description": "Calcule un chiffre sur le jeu de séries IMDb nettoyé. "
                       "count compte les séries ; median et max portent sur une colonne ; "
                       "percent donne la part des séries où la colonne est renseignée.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["count", "median", "max", "percent"]},
                "column": {"type": "string",
                           "enum": ["startYear", "endYear", "runtimeMinutes", "averageRating", "numVotes"],
                           "description": "Obligatoire sauf pour count."},
                "year": {"type": "integer", "description": "Année de début de la série."},
                "genre": {"type": "string", "description": "Genre IMDb en anglais, par exemple Drama ou Comedy."},
                "reliable_only": {"type": "boolean", "description": "Seulement les séries avec au moins 1000 votes."},
            },
            "required": ["operation"],
        },
    },
}

ALLOWED_ARGS = {"operation", "column", "year", "genre", "reliable_only"}


def call_ollama(messages):
    """Envoie la conversation à Qwen et renvoie son message de réponse."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": [TOOL],
        "stream": False,
        "think": False,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()["message"]


def run_tool(name, args, df):
    """Exécute l'outil demandé par le modèle, ou renvoie une erreur."""
    if name != "compute":
        return {"error": f"outil inconnu : {name}. Seul outil disponible : compute"}
    unknown = set(args) - ALLOWED_ARGS
    if unknown:
        return {"error": f"paramètres inconnus : {sorted(unknown)}. Permis : {sorted(ALLOWED_ARGS)}"}
    if "operation" not in args:
        return {"error": "le paramètre operation est obligatoire"}
    return compute(df, **args)


def ask(question, df, chat=call_ollama, max_turns=MAX_TURNS):
    """Boucle : le modèle demande des calculs, le code les exécute, jusqu'à une réponse en texte."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = {"question": question, "model": MODEL, "steps": [], "answer": None, "error": None}
    start = time.time()

    for _ in range(max_turns):
        reply = chat(messages)
        messages.append(reply)
        calls = reply.get("tool_calls") or []

        if not calls:
            trace["answer"] = reply.get("content", "")
            break

        for call in calls:
            name = call["function"]["name"]
            args = call["function"].get("arguments") or {}
            result = run_tool(name, args, df)
            trace["steps"].append({"tool": name, "arguments": args, "result": result})
            messages.append({"role": "tool", "tool_name": name,
                             "content": json.dumps(result, ensure_ascii=False)})
    else:
        trace["error"] = f"limite de {max_turns} tours atteinte sans réponse finale"

    trace["seconds"] = round(time.time() - start, 1)
    return trace


def save_trace(trace):
    TRACES_DIR.mkdir(exist_ok=True)
    path = TRACES_DIR / f"{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
    path.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage : python agent.py "ta question"')
        sys.exit(1)
    trace = ask(sys.argv[1], load_series())
    for step in trace["steps"]:
        print(f"Appel : {step['tool']}({step['arguments']}) -> {step['result']}")
    print("Réponse :", trace["answer"] or trace["error"])
    print("Trace :", save_trace(trace))
