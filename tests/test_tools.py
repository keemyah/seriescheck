import pandas as pd
import pytest
from tools import compute

# 8 séries inventées, lignes numérotées de 0 à 7
# 0: 2015, fin 2018, Drama, 8.0, fiable
# 1: 2015, en cours, Drama+Crime, 7.0, fiable
# 2: 2015, fin 2016, Comedy, 6.0, non fiable
# 3: 2016, en cours, Musical, 9.0, fiable
# 4: 2016, fin 2017, Music+Comedy, 5.0, fiable
# 5: 2014, fin 2015, sans genre, sans note, non fiable
# 6: 2015, en cours, Drama, 7.5, fiable
# 7: sans année, en cours, Comedy, sans note, non fiable


@pytest.fixture
def df():
    return pd.DataFrame({
        "startYear": [2015, 2015, 2015, 2016, 2016, 2014, 2015, None],
        "endYear": [2018, None, 2016, None, 2017, 2015, None, None],
        "runtimeMinutes": [45, 50, 30, 60, 25, None, 40, 30],
        "genres": ["Drama", "Drama,Crime", "Comedy", "Musical", "Music,Comedy", None, "Drama", "Comedy"],
        "averageRating": [8.0, 7.0, 6.0, 9.0, 5.0, None, 7.5, None],
        "numVotes": [2000, 1500, 300, 5000, 1200, None, 1000, None],
        "note_fiable": [True, True, False, True, True, False, True, False],
    })


def test_count_year(df):
    assert compute(df, "count", year=2015)["result"] == 4


def test_count_year_given_as_text(df):
    assert compute(df, "count", year="2015")["result"] == 4


def test_count_genre_and_year(df):
    assert compute(df, "count", genre="Drama", year=2015)["result"] == 3


def test_genre_match_is_exact(df):
    assert compute(df, "count", genre="Music")["result"] == 1


def test_median_reliable_only(df):
    out = compute(df, "median", column="averageRating", reliable_only=True)
    assert out["result"] == 7.5
    assert out["rows_used"] == 5


def test_max_reliable_only(df):
    assert compute(df, "max", column="averageRating", reliable_only=True)["result"] == 9.0


def test_percent_with_end_year(df):
    assert compute(df, "percent", column="endYear")["result"] == 50.0


def test_count_genre_reliable(df):
    assert compute(df, "count", genre="Comedy", reliable_only=True)["result"] == 1


def test_count_no_match_gives_zero(df):
    assert compute(df, "count", genre="Western")["result"] == 0


def test_median_no_match_gives_error(df):
    assert "error" in compute(df, "median", column="averageRating", genre="Western")


def test_unknown_operation(df):
    assert "error" in compute(df, "delete", column="averageRating")


def test_unknown_column(df):
    assert "error" in compute(df, "median", column="titre")


def test_median_needs_a_column(df):
    assert "error" in compute(df, "median")
