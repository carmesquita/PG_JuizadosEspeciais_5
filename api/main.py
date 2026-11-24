from functools import lru_cache
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from contextlib import asynccontextmanager
from typing import Literal
from src.conversa_llm import carregar_modelo_conversa, responder_conversa
from openai import APITimeoutError


PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_TRIBUNAIS = (
    PASTA_PROJETO
    / "data"
    / "processed"
    / "tempo_sentenca_juizados.csv"
)


class Tribunal(BaseModel):
    ano: int
    tribunal: str
    nome_tribunal: str
    uf: str
    tempo_medio_sentenca_dias: float
    sentencas_conhecimento: int


class ObservacaoEntrada(BaseModel):
    tribunal: str = Field(min_length=2, max_length=10)
    observacao: str = Field(min_length=5, max_length=500)
    fonte: str = Field(min_length=2, max_length=200)

class ObservacaoResposta(ObservacaoEntrada):
    id: int

#classe alterada para tratamento dos erros
class MensagemConversa(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

class TextoEntrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    texto: str = Field(min_length=1)
    historico: list[MensagemConversa]

class ComparacaoResposta(BaseModel):
    texto: str
    tipo_analise: str
    resultado: str

class InicioResposta(BaseModel):
    mensagem: str
    documentacao: str

MOTORES = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        MOTORES["conversa"] = carregar_modelo_conversa()
    except (OSError, ValueError, KeyError) as falha:
        MOTORES["conversa"] = None
        print(f"Conversa indisponível: {falha}")

    yield
    MOTORES.clear()

app = FastAPI(
    lifespan=lifespan,
    title="API dos Juizados Especiais",
    description=(
        "API para consulta dos dados dos Tribunais de Justiça e "
        "recebimento de informações complementares."
    ),
    version="1.0.0",
)

#Correção do feedback no TP3 - recuperar as observações salvas em CSV.
ARQUIVO_OBSERVACOES = PASTA_PROJETO / "data" / "observacoes.csv"

observacoes = []

if ARQUIVO_OBSERVACOES.exists():
    observacoes = pd.read_csv(
        ARQUIVO_OBSERVACOES,
        dtype="string",
    ).to_dict(orient="records")

@lru_cache
def carregar_tribunais() -> pd.DataFrame:
    return pd.read_csv(ARQUIVO_TRIBUNAIS)


@app.get(
    "/",
    response_model=InicioResposta,
    tags=["Status"],
    summary="Apresentar informações da API",
)
def inicio():
    return {
        "mensagem": "API dos Juizados Especiais em funcionamento.",
        "documentacao": "/docs",
    }


@app.get(
    "/tribunais",
    response_model=list[Tribunal],
    tags=["Tribunais"],
    summary="Listar todos os tribunais",
)
def listar_tribunais():
    dados = carregar_tribunais()
    return dados.to_dict(orient="records")


@app.get(
    "/tribunais/{sigla}",
    response_model=Tribunal,
    tags=["Tribunais"],
    summary="Consultar um tribunal pela sigla",
)
def consultar_tribunal(sigla: str):
    dados = carregar_tribunais()
    sigla = sigla.strip().upper()

    resultado = dados.loc[dados["tribunal"] == sigla]

    if resultado.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tribunal não encontrado.",
        )

    return resultado.iloc[0].to_dict()


@app.post(
    "/observacoes",
    response_model=ObservacaoResposta,
    status_code=status.HTTP_201_CREATED,
    tags=["Observações"],
    summary="Receber uma informação complementar",
)
def criar_observacao(observacao: ObservacaoEntrada):
    tribunal = observacao.tribunal.strip().upper()
    texto = observacao.observacao.strip()
    fonte = observacao.fonte.strip()

    if not texto or not fonte:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A observação e a fonte não podem ficar vazias.",
        )

    dados = carregar_tribunais()

    if tribunal not in dados["tribunal"].values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tribunal não encontrado.",
        )

    registro = ObservacaoResposta(
        id=len(observacoes) + 1,
        tribunal=tribunal,
        observacao=texto,
        fonte=fonte,
    )
    #Correção
    observacoes.append(registro.model_dump())
    pd.DataFrame(observacoes).to_csv(ARQUIVO_OBSERVACOES, index=False)
    return registro


@app.post(
    "/processar_texto",
    response_model=ComparacaoResposta,
    tags=["Conversa"],
    summary="Conversar sobre os dados dos tribunais",
)
def processar_texto(pedido: TextoEntrada):
    if MOTORES["conversa"] is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "O modelo de conversa está indisponível. "
                "As consultas aos tribunais continuam disponíveis."
            ),
        )

    try:
        #temporário do 500 solicitado no feedback do TP4.
        #raise ValueError("Falha simulada durante a geração.")
        resultado = responder_conversa(
            MOTORES["conversa"],
            pedido.texto,
            [mensagem.model_dump() for mensagem in pedido.historico],
            carregar_tribunais(),
        )
    except APITimeoutError:
        #feedback do TP4: demora excessiva retorna 504.
        raise HTTPException(
            status_code=504,
            detail="O tempo de espera pelo modelo foi excedido. Tente novamente.",
        )

    except Exception as falha:
        # Feedback do TP4: falhas durante a geração retornam 500.
        print(f"Falha ao consultar o modelo: {falha}")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível gerar a resposta. Tente novamente.",
        )

    if not resultado:
        raise HTTPException(
            status_code=500,
            detail="O modelo não retornou uma resposta. Tente novamente.",
        )

    return {
        "texto": pedido.texto,
        "tipo_analise": "conversa",
        "resultado": resultado,
    }