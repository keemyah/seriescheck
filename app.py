"""Interface web de SeriesCheck : la même boucle que python agent.py, dans le navigateur.

Usage : streamlit run app.py   (Ollama doit être lancé)
Streamlit relance tout ce fichier à chaque interaction : l'historique est donc
gardé dans st.session_state, et les données dans un cache (@st.cache_data).
"""
import requests
import streamlit as st

from agent import ask, save_trace
from tools import load_series

st.set_page_config(page_title="SeriesCheck")
st.title("SeriesCheck")
st.caption("Questions chiffrées sur les séries TV (données IMDb). "
           "Tout chiffre qui n'a pas été calculé par l'outil est refusé par l'arbitre.")


@st.cache_data
def get_series():
    """Chargé une seule fois, puis réutilisé à chaque relance du fichier."""
    return load_series()


def show(trace):
    """Affiche une réponse : vert si l'arbitre l'accepte, rouge s'il la refuse."""
    verdict = trace.get("verdict")
    if verdict is None:  # pas de réponse en texte (par exemple : nombre maximum de tours atteint)
        st.warning(trace["final"])
    elif verdict["accepted"]:
        st.success(trace["final"])
    else:
        st.error(trace["final"])
    with st.expander("Détails"):
        for step in trace["steps"]:
            st.write(f"Appel : `{step['tool']}({step['arguments']})` → `{step['result']}`")
        st.write("Réponse du modèle :", trace["answer"])
        st.write(f"Durée : {trace['seconds']} s, trace : `{trace['file']}`")


df = get_series()
if "history" not in st.session_state:
    st.session_state.history = []  # liste de (question, trace), gardée entre deux relances

for question, trace in st.session_state.history:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        show(trace)

question = st.chat_input("Ta question, par exemple : Combien de séries Drama ont commencé en 2015 ?")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Qwen réfléchit…"):
                trace = ask(question, df)
        except requests.RequestException as error:
            st.error(f"Ollama ne répond pas : {error}")
        else:
            trace["file"] = str(save_trace(trace))
            show(trace)
            st.session_state.history.append((question, trace))
