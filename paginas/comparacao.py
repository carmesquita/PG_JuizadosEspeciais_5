import requests
import streamlit as st

from comum import URL_API, carregar_dados, iniciar_estado


dados, _ = carregar_dados()
iniciar_estado()

st.title("Comparação entre tribunais")

coluna1, coluna2 = st.columns(2)

limite = coluna1.slider(
    "Mostrar tribunais com tempo de até",
    min_value=90,
    max_value=420,
    value=st.session_state["limite"],
    step=10,
    format="%d dias",
)
st.session_state["limite"] = limite

opcoes_ordem = [
    "Menor tempo primeiro",
    "Maior tempo primeiro",
]

ordem = coluna2.selectbox(
    "Ordenar o resultado",
    opcoes_ordem,
    index=opcoes_ordem.index(st.session_state["ordem"]),
)
st.session_state["ordem"] = ordem

filtrados = dados.loc[
    dados["tempo_medio_sentenca_dias"] <= limite
].copy()

filtrados = filtrados.sort_values(
    "tempo_medio_sentenca_dias",
    ascending=ordem == "Menor tempo primeiro",
)

st.bar_chart(
    filtrados,
    x="tribunal",
    y="tempo_medio_sentenca_dias",
    x_label="Tribunal",
    y_label="Tempo médio em dias",
)

st.dataframe(
    filtrados[
        [
            "tribunal",
            "uf",
            "tempo_medio_sentenca_dias",
            "sentencas_conhecimento",
        ]
    ].rename(
        columns={
            "tribunal": "Tribunal",
            "uf": "UF",
            "tempo_medio_sentenca_dias": "Tempo médio da sentença",
            "sentencas_conhecimento": "Sentenças de conhecimento",
        }
    ),
    hide_index=True,
)

st.download_button(
    "Baixar dados filtrados",
    filtrados.to_csv(index=False).encode("utf-8-sig"),
    "tempo_sentenca_juizados.csv",
    "text/csv",
)

st.subheader("Consulta e comparação")

tribunal_selecionado = st.selectbox(
    "Selecione um tribunal",
    sorted(dados["tribunal"]),
)

linha_selecionada = dados.loc[
    dados["tribunal"] == tribunal_selecionado
].iloc[0]

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric(
        f"Tempo no {tribunal_selecionado}",
        f"{linha_selecionada['tempo_medio_sentenca_dias']:.1f} dias",
    )

with coluna2:
    st.metric(
        "Sentenças de conhecimento",
        f"{linha_selecionada['sentencas_conhecimento']:,.0f}".replace(",", "."),
    )

if st.button("Adicionar à comparação"):
    if tribunal_selecionado not in st.session_state["comparacao"]:
        st.session_state["comparacao"].append(tribunal_selecionado)

if st.session_state["comparacao"]:
    st.dataframe(
        dados.loc[
            dados["tribunal"].isin(st.session_state["comparacao"]),
            [
                "tribunal",
                "tempo_medio_sentenca_dias",
                "sentencas_conhecimento",
            ],
        ],
        hide_index=True,
    )

    if st.button("Limpar comparação"):
        st.session_state["comparacao"].clear()
        st.rerun()


st.subheader("Conversa sobre os tribunais")
st.write("Pergunte sobre o tempo médio até a sentença em 2025.")

for mensagem in st.session_state["conversa"]:
    if mensagem["role"] == "user":
        st.write(f"**Você:** {mensagem['content']}")
    else:
        st.write(f"**Assistente:** {mensagem['content']}")

pergunta = st.chat_input("Digite sua pergunta sobre os tribunais")

if pergunta:
    try:
        resposta = requests.post(
            f"{URL_API}/processar_texto",
            json={
                "texto": pergunta,
                "historico": st.session_state["conversa"],
            },
            timeout=60,
        )

        if resposta.status_code == 200:
            st.session_state["conversa"].append(
                {"role": "user", "content": pergunta}
            )
            st.session_state["conversa"].append(
                {
                    "role": "assistant",
                    "content": resposta.json()["resultado"],
                }
            )
            st.rerun()
        else:
            st.error(
                f"A API retornou o erro {resposta.status_code}: "
                f"{resposta.json().get('detail', 'Erro não identificado.')}"
            )

    except requests.RequestException:
        st.error(
            "Não foi possível consultar a API. "
            "Verifique o terminal do FastAPI e tente novamente."
        )        