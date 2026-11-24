from pathlib import Path
import pandas as pd

from conversa_llm import carregar_modelo_conversa, responder_conversa


# O teste com três tribunais funcionou. Agora usamos o CSV completo.
dados = pd.read_csv(
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "tempo_sentenca_juizados.csv"
)

print("Tribunais carregados:", len(dados))

modelo = carregar_modelo_conversa()
historico = []

for pergunta in [
    "Qual é o tempo médio até a sentença do TJAC em 2025?",
    "Qual tribunal eu citei na pergunta anterior?",
]:
    print("\nPergunta:", pergunta)

    resposta = responder_conversa(modelo, pergunta, historico, dados)

    print("Resposta:", resposta)

    historico.append({"role": "user", "content": pergunta})
    historico.append({"role": "assistant", "content": resposta})