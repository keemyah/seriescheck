from arbiter import check, extract_numbers

QUESTION = "Combien de séries Drama ont commencé en 2015 ?"
STEPS = [{"tool": "compute", "arguments": {}, "result": {"result": 1591, "rows_used": 1591}}]


# Extraction des nombres

def test_extract_simple():
    assert extract_numbers("1591 séries en 2015") == [1591.0, 2015.0]


def test_extract_thousands_with_space():
    assert extract_numbers("1 591 séries") == [1591.0]


def test_extract_thousands_with_non_breaking_space():
    assert extract_numbers("1\u00a0591 séries") == [1591.0]


def test_extract_decimal_comma():
    assert extract_numbers("note médiane de 7,3") == [7.3]


def test_extract_decimal_point_and_percent():
    assert extract_numbers("39.6 % des séries") == [39.6]


def test_extract_number_at_end_of_sentence():
    assert extract_numbers("Il y en a 1591.") == [1591.0]


def test_extract_no_number():
    assert extract_numbers("Je ne sais pas") == []


def test_extract_ignores_digits_inside_words():
    assert extract_numbers("le modèle qwen35") == []


# Verdicts de l'arbitre

def test_accepts_number_from_tool():
    assert check("Il y a eu 1591 séries.", QUESTION, STEPS)["accepted"]


def test_accepts_number_from_question():
    assert check("En 2015, il y a eu 1 591 séries Drama.", QUESTION, STEPS)["accepted"]


def test_refuses_invented_number():
    verdict = check("Il y a eu environ 1600 séries.", QUESTION, STEPS)
    assert not verdict["accepted"]
    assert verdict["unverified"] == [1600.0]


def test_refuses_rounded_number():
    steps = [{"tool": "compute", "arguments": {}, "result": {"result": 39.6, "rows_used": 304181}}]
    assert not check("Environ 40 % des séries.", "Quelle part ?", steps)["accepted"]


def test_accepts_same_decimal_written_differently():
    steps = [{"tool": "compute", "arguments": {}, "result": {"result": 7.3, "rows_used": 10382}}]
    assert check("La note médiane est 7,30 sur 10 382 séries.", "Note médiane ?", steps)["accepted"]


def test_accepts_context_numbers():
    steps = [{"tool": "compute", "arguments": {}, "result": {"result": 7.3, "rows_used": 10382}}]
    answer = "La note médiane des séries avec au moins 1 000 votes est de 7,3 sur 10."
    assert check(answer, "Note médiane ?", steps)["accepted"]


def test_context_numbers_do_not_open_the_door_to_others():
    steps = [{"tool": "compute", "arguments": {}, "result": {"result": 7.3, "rows_used": 10382}}]
    verdict = check("Une note de 7,5 sur 10.", "Note médiane ?", steps)
    assert verdict["unverified"] == [7.5]


def test_refuses_any_number_when_no_tool_was_called():
    assert not check("Il y a eu 1591 séries.", QUESTION, [])["accepted"]


def test_accepts_answer_without_number():
    assert check("Je ne sais pas.", QUESTION, [])["accepted"]


def test_tool_error_gives_no_allowed_number():
    steps = [{"tool": "compute", "arguments": {}, "result": {"error": "aucune ligne"}}]
    assert not check("Il y a 12 séries.", QUESTION, steps)["accepted"]
