# PB Juizados Especiais — TP5

**Autora:** Carolina Gabriela Mesquita.

Projeto acadêmico para comparar o tempo médio até a sentença nos Juizados Especiais dos 27 Tribunais de Justiça, utilizando dados de 2025 do CNJ.

A etapa 5 integra memória conversacional ao painel, permitindo consultar os dados e fazer perguntas encadeadas sobre os tribunais. A proposta está relacionada à ODS 16, por facilitar a compreensão e a leitura transparente de indicadores públicos da Justiça.

## Funcionalidades

- painel Streamlit com quatro páginas;
- consultas, filtros, tabelas, gráficos e download de CSV;
- dados estatísticos obtidos pelo GET `/tribunais`;
- notícias do CNJ como informações de contexto;
- recebimento de observações pela API e armazenamento em `data/observacoes.csv`;
- memória conversacional na página Comparação entre tribunais;
- perguntas e histórico enviados ao POST `/processar_texto`;
- respostas estruturadas com Pydantic e tratamento de erros.

## Modelo e memória conversacional

O modelo utilizado é `nvidia/nemotron-3.5-lightning:free`, acessado pelo OpenRouter com ChatOpenAI.

A escolha ocorreu após os testes com o TinyLlama apresentarem falhas na recuperação do contexto. Os experimentos anteriores foram preservados como histórico do projeto.

O modelo recebe fatos contendo ano, sigla e tempo médio dos 27 tribunais. Também recebe o histórico da conversa e notas com as siglas mencionadas nas perguntas anteriores.

O prompt orienta respostas curtas em português, utilização dos fatos fornecidos e preservação das siglas.


## Bibliotecas utilizadas

| Biblioteca | Uso no projeto |
|---|---|
| streamlit | Interface, gráficos e histórico da sessão |
| pandas | Preparação dos dados e manipulação de tabelas |
| requests | Coleta HTTP e comunicação do painel com a API |
| beautifulsoup4 | Extração das informações das notícias |
| fastapi | Rotas da API |
| pydantic | Validação dos dados de entrada e saída |
| uvicorn | Execução do servidor da API |
| langchain-openai | Integração com o modelo por meio de ChatOpenAI |
| openai | Cliente utilizado pela integração e tratamento de APITimeoutError |

A instalação utiliza requirements-api.txt, que também inclui requirements.txt.

## Instalação e execução

Na pasta do projeto, crie o ambiente virtual, ative-o e instale as dependências:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-api.txt
```

Nesse mesmo terminal, configure sua chave privada e inicie a API. Substitua SUA_CHAVE pela sua chave somente no terminal:

```powershell
$env:OPENROUTER_API_KEY = "SUA_CHAVE"
uvicorn api.main:app
```

Aguarde a inicialização da API. A chave deve permanecer fora do código compartilhado.

Em outro terminal, na mesma pasta do projeto, ative o ambiente e inicie o painel:

```powershell
.venv\Scripts\activate
streamlit run app.py
```

Os dois processos precisam permanecer em execução.

Endereços locais padrão:

- [Aplicativo Streamlit](http://localhost:8501)
- [Documentação da API](http://127.0.0.1:8000/docs)


## Uso da conversa no painel

Entre na página Comparação entre tribunais e utilize o campo de perguntas.

Exemplos verificados na mesma conversa:

1. Qual é o tempo médio até a sentença do TJAC em 2025?
2. Qual tribunal eu citei na pergunta anterior?
3. Compare esse tribunal com o TJSE em 2025. Qual teve o menor tempo médio até a sentença e qual foi a diferença em dias?

As respostas informaram 129,6 dias para o TJAC, recuperaram sua sigla na pergunta seguinte e identificaram o TJSE como o tribunal com menor tempo: 111,7 dias, com diferença de 17,9 dias.

As perguntas e respostas permanecem no histórico da sessão e são reenviadas ao modelo nas próximas interações.

## Consulta pela documentação da API

Para iniciar uma conversa pelo POST `/processar_texto`, utilize:

```json
{
  "texto": "Qual é o tempo médio até a sentença do TJAC em 2025?",
  "historico": []
}
```

O histórico começa vazio na primeira pergunta. Nas seguintes, deve conter as mensagens anteriores com os campos `role` e `content`.

A resposta contém `texto`, `tipo_analise` e `resultado`, com `tipo_analise` igual a `conversa`.

A rota /processar_texto trata os seguintes casos:

| Código | Situação |
|---|---|
| 422 | Entrada inválida |
| 503 | Modelo não inicializado |
| 500 | Falha durante a geração ou ausência de resposta |
| 504 | Timeout na requisição ao modelo |

A requisição ao modelo está configurada com timeout de 30 segundos e sem repetições automáticas.

O retorno 500 foi verificado com uma falha simulada antes da geração. O retorno 504 foi verificado reduzindo temporariamente o timeout para 0.001 segundo.

## Ajustes decorrentes do feedback do TP3

- O GET passou a alimentar tabelas e gráficos.
- As observações passaram a ser gravadas em CSV e recuperadas na inicialização.
- O uso efetivo do LLM foi registrado no Project Charter e no Data Summary Report.
- O endereço local da API foi centralizado em `comum.py`.

## Limitações

- A base estatística contempla somente 2025.
- O indicador é agregado por tribunal e não representa a duração de processos individuais nem explica as causas das diferenças.
- Os testes realizados abrangem poucos exemplos. As respostas devem ser conferidas com os dados.
- O histórico é mantido durante a sessão do Streamlit.
- A conversa depende da conexão com a internet, da chave configurada e da disponibilidade da API do modelo.
- A configuração atual é destinada à execução local.

## Fontes e apoio

- Conselho Nacional de Justiça — Justiça em Números e notícias dos Juizados Especiais.
- Organização das Nações Unidas — ODS 16.
- Materiais das disciplinas Projeto de Bloco, Desenvolvimento Data Driven Python e Engenharia de Prompts para Ciência de Dados.
- ChatGPT — apoio na orientação do código, revisão dos textos e complementação da documentação. A execução da aplicação e a conferência dos resultados foram realizadas pela autora.