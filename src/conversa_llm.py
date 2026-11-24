import os
from langchain_openai import ChatOpenAI


def carregar_modelo_conversa():
    return ChatOpenAI(
        model="nvidia/nemotron-3.5-lightning:free",
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        max_tokens=1500,
        #feedback do TP4 - configurar o tempo de espera.
        timeout=30, #timeout=0.001, #teste erro 504 #timeout=30,
        max_retries=0,
    )

def responder_conversa(modelo, pergunta, historico, dados):
    sistema = """Você responde perguntas sobre os Juizados Especiais em português.
Use somente os fatos fornecidos, sem expandir as siglas.
Se faltar informação para entender a pergunta, peça esclarecimento.
Responda em uma frase curta.

TEMPO MÉDIO ATÉ A SENTENÇA
"""

    for linha in dados.to_dict("records"):
        sistema += (
            f"\n{linha['tribunal']} ({linha['ano']}): "
            f"{linha['tempo_medio_sentenca_dias']} dias."
        )

    notas = []

    for mensagem in historico:
        if mensagem["role"] == "user":
            for sigla in dados["tribunal"]:
                if sigla in mensagem["content"]:
                    notas.append(sigla)

    if notas:
        sistema += (
            "\nTribunais mencionados nas perguntas anteriores: "
            + ", ".join(notas)
        )

    return modelo.invoke(
        [{"role": "system", "content": sistema}]
        + historico
        + [{"role": "user", "content": pergunta}]
    ).content