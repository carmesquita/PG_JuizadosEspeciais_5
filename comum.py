from pathlib import Path
import requests
import pandas as pd
import streamlit as st


PASTA_PROJETO = Path(__file__).resolve().parent
CAMPOS_COMPLEMENTARES = ["tribunal", "observacao", "fonte"]
URL_API = "http://127.0.0.1:8000"

# Correção indicada pelo professor no feedback do TP3: 
@st.cache_data
def carregar_dados():
    try:
        resposta = requests.get(f"{URL_API}/tribunais", timeout=10)
        resposta.raise_for_status()
    except requests.RequestException:
        st.error(
            "Não foi possível consultar a API. "
            "Verifique se o FastAPI está em execução."
        )
        st.stop()

    dados = pd.DataFrame(resposta.json())

    noticias = pd.read_csv(
        PASTA_PROJETO / "data" / "processed" / "noticias_juizados.csv"
    )

    return dados, noticias


def iniciar_estado():
    st.session_state.setdefault("comparacao", [])
    st.session_state.setdefault(
        "dados_complementares",
        pd.DataFrame(columns=CAMPOS_COMPLEMENTARES),
    )
    st.session_state.setdefault("limite", 420)
    st.session_state.setdefault("ordem", "Menor tempo primeiro")
    st.session_state.setdefault("conversa", [])