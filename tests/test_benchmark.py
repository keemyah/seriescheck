import pandas as pd
import pytest
from benchmark import grade, run_alone, summarize
from expected import expected_answers
from tools import compute


# Notation d'une réponse

def test_grade_right_answer():
    assert grade("Il y a eu 1 591 séries.", 1591) == "juste"


def test_grade_right_decimal_written_with_comma():
    assert grade("La note médiane est 7,3.", 7.3) == "juste"


def test_grade_wrong_answer():
    assert grade("Environ 1600 séries.", 1591) == "faux"


def test_grade_close_decimal_is_wrong():
    assert grade("La note médiane est 7,25.", 7.3) == "faux"


def test_grade_refused_by_arbiter():
    assert grade("Réponse refusée : chiffre non calculé [1600.0]", 1600, refused=True) == "refusé"


def test_grade_no_number_counts_as_refused():
    assert grade("Je ne sais pas.", 1591) == "refusé"


def test_grade_number_from_question_is_not_an_answer():
    question = "Combien de séries ont commencé en 2015 ?"
    answer = "Je ne connais pas les séries de 2015."
    assert grade(answer, 11333, question=question) == "refusé"


def test_grade_invented_number_still_wrong_with_question():
    question = "Combien de séries ont commencé en 2015 ?"
    assert grade("Plus de 600 séries en 2015.", 11333, question=question) == "faux"


# Qwen seul : aucun outil n'est envoyé

def test_alone_sends_no_tool():
    received = {}

    def chat(messages, tools):
        received["tools"] = tools
        return {"role": "assistant", "content": "Environ 500."}

    answer, refused, _ = run_alone("Combien ?", chat=chat)
    assert received["tools"] == ()
    assert answer == "Environ 500."
    assert not refused


# Résumé : moyenne et écart-type

def test_summarize_mean_and_std():
    rows = []
    for run, n_right in [(1, 2), (2, 4), (3, 3)]:
        for task in range(1, 5):
            for name in ["systeme", "qwen_seul"]:
                verdict = "juste" if name == "systeme" and task <= n_right else "faux"
                rows.append({"run": run, "candidate": name, "task": task, "verdict": verdict})
    summary = summarize(rows, 4)
    assert summary["systeme"]["justes_par_lancement"] == [2, 4, 3]
    assert summary["systeme"]["moyenne"] == 3
    assert summary["systeme"]["ecart_type"] == 1.0
    assert summary["qwen_seul"]["total_faux"] == 12


# Réponses attendues : calculées par une autre voie, elles doivent égaler l'outil

@pytest.fixture
def df():
    return pd.DataFrame({
        "startYear": [2015, 2015, 2015, 2020, 2010, 2010, 2010, None],
        "endYear": [2018, None, 2016, None, 2012, None, None, None],
        "genres": ["Drama", "Drama,Crime", "Comedy", "Musical", "Comedy,Crime", None, "Drama", "Comedy"],
        "averageRating": [8.0, 7.0, 6.0, 9.0, 5.0, None, 7.5, None],
        "numVotes": [2000, 1500, 300, 5000, 1200, None, 1000, None],
        "note_fiable": [True, True, False, True, True, False, True, False],
    })


def test_expected_answers_by_hand(df):
    exp = expected_answers(df)
    assert exp[1] == 3
    assert exp[2] == 2
    assert exp[3] == 7.5
    assert exp[6] == 1
    assert exp[8] == 2
    assert exp[9] == 1500.0
    assert exp[10] == 33.3


def test_expected_answers_agree_with_tool(df):
    exp = expected_answers(df)
    assert exp[1] == compute(df, "count", year=2015)["result"]
    assert exp[2] == compute(df, "count", genre="Drama", year=2015)["result"]
    assert exp[4] == compute(df, "max", column="averageRating", reliable_only=True)["result"]
    assert exp[5] == compute(df, "percent", column="endYear")["result"]
    assert exp[7] == compute(df, "count", year=2020)["result"]
    assert exp[9] == compute(df, "median", column="numVotes", reliable_only=True)["result"]
    assert exp[10] == compute(df, "percent", column="endYear", year=2010)["result"]
