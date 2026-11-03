import pandas as pd
import pytest
from agent import ask, run_tool

# Ces tests n'appellent jamais Qwen : un faux modèle renvoie des réponses écrites à l'avance.


@pytest.fixture
def df():
    return pd.DataFrame({
        "startYear": [2015, 2015, 2016],
        "endYear": [2018, None, None],
        "runtimeMinutes": [45, 50, 60],
        "genres": ["Drama", "Comedy", "Drama"],
        "averageRating": [8.0, 6.0, 9.0],
        "numVotes": [2000, 300, 5000],
        "note_fiable": [True, False, True],
    })


def tool_call(name, arguments):
    return {"role": "assistant", "content": "",
            "tool_calls": [{"function": {"name": name, "arguments": arguments}}]}


def fake_model(replies):
    """Renvoie les réponses de la liste une par une, comme si c'était le modèle."""
    replies = list(replies)
    return lambda messages: replies.pop(0)


def test_tool_is_executed_then_answer(df):
    chat = fake_model([
        tool_call("compute", {"operation": "count", "year": 2015}),
        {"role": "assistant", "content": "2 séries ont commencé en 2015."},
    ])
    trace = ask("Combien ?", df, chat=chat)
    assert trace["steps"][0]["result"] == {"result": 2, "rows_used": 2}
    assert trace["answer"] == "2 séries ont commencé en 2015."
    assert trace["error"] is None


def test_answer_without_tool(df):
    chat = fake_model([{"role": "assistant", "content": "Bonjour"}])
    trace = ask("Salut", df, chat=chat)
    assert trace["steps"] == []
    assert trace["answer"] == "Bonjour"


def test_loop_stops_after_max_turns(df):
    chat = lambda messages: tool_call("compute", {"operation": "count"})
    trace = ask("Combien ?", df, chat=chat, max_turns=3)
    assert len(trace["steps"]) == 3
    assert trace["answer"] is None
    assert "limite" in trace["error"]


def test_tool_result_is_sent_back_to_model(df):
    seen = []

    def chat(messages):
        seen.append(list(messages))
        if len(seen) == 1:
            return tool_call("compute", {"operation": "count", "genre": "Drama"})
        return {"role": "assistant", "content": "2"}

    ask("Combien de Drama ?", df, chat=chat)
    last_message = seen[1][-1]
    assert last_message["role"] == "tool"
    assert '"result": 2' in last_message["content"]


def test_unknown_tool_is_refused(df):
    assert "error" in run_tool("delete_files", {}, df)


def test_unknown_argument_is_refused(df):
    assert "error" in run_tool("compute", {"operation": "count", "path": "/"}, df)


def test_missing_operation_is_refused(df):
    assert "error" in run_tool("compute", {"year": 2015}, df)
