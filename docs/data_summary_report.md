# Data Summary Report — TP5 Juizados Especiais

**Autora:** Carolina Gabriela Mesquita.

## Fontes e finalidade dos dados

| Fonte | Tipo | Finalidade |
|---|---|---|
| Justiça em Números/CNJ | CSV disponibilizado em ZIP | comparar o tempo médio até a sentença nos Juizados Especiais |
| Notícias dos Juizados Especiais/CNJ | HTML | apresentar informações de contexto |
| CSV enviado pelo usuário | CSV estruturado | acrescentar informações complementares |
| Observações enviadas pela API | JSON armazenado em CSV | registrar observações separadamente da base oficial |

## Coleta e preparação dos dados estatísticos

O notebook `extrair_justica_em_numeros.ipynb` baixa o ZIP disponibilizado pelo CNJ e preserva o arquivo bruto em `data/raw`.

A leitura considera o separador, a codificação e o formato decimal da base. As marcações `nd` e `n/a` são reconhecidas como valores ausentes.

Em seguida, o notebook:

- seleciona o ano de 2025 e a Justiça Estadual, excluindo a sigla genérica `TJ`;
- seleciona e renomeia os campos utilizados pelo projeto;
- arredonda o tempo médio para uma casa decimal;
- ordena os tribunais pelo indicador;
- salva `tempo_sentenca_juizados.csv` em `data/processed`.

O arquivo contém ano, sigla e nome do tribunal, UF, tempo médio até a sentença e quantidade de sentenças de conhecimento.

## Coleta e preparação das notícias

O notebook `coletar_noticias_juizados.ipynb` utiliza requisições HTTP e Beautiful Soup para coletar dez registros da página do CNJ.
São extraídos título, data, trecho apresentado na página, URL e fonte. O HTML bruto é preservado, e os registros são salvos em `noticias_juizados.csv`.
O arquivo `noticias_para_llm.csv`, preparado anteriormente, reúne títulos e trechos com espaços normalizados e mantém os identificadores e a origem. Esses trechos não são artigos completos nem resumos produzidos pelo modelo.
As notícias permanecem como contexto. O foco principal do projeto é a comparação dos indicadores dos Juizados Especiais.

## Verificações existentes

Os notebooks verificam:

- 27 registros e 27 siglas distintas na base estatística;
- tempos médios presentes e positivos;
- dez notícias, com títulos presentes e URLs distintas.

## Integração com a aplicação

A API lê a base estatística processada e disponibiliza os dados pelo GET `/tribunais`. O Streamlit utiliza esse retorno para alimentar tabelas, gráficos e consultas.

As observações recebidas pelo POST `/observacoes` são gravadas em `data/observacoes.csv` e recuperadas na inicialização da API, mantendo-se separadas dos indicadores oficiais.

## Uso de IA e resultados da etapa 5

Na etapa 4, o TinyLlama foi utilizado para produzir explicações sobre comparações fornecidas na entrada. Nos testes de memória conversacional da etapa 5, esse modelo apresentou falhas na recuperação do contexto.

A solução final utiliza memória conversacional com o modelo nvidia/nemotron-3.5-lightning:free, acessado pelo OpenRouter com ChatOpenAI e integrado à página de comparação entre tribunais.

A base processada dos 27 tribunais é transformada em fatos contendo ano, sigla e tempo médio até a sentença. O Python também identifica as siglas mencionadas nas perguntas anteriores e as fornece como notas ao modelo.

O histórico permanece na sessão do Streamlit. A cada pergunta, a aplicação envia o texto e o histórico ao POST `/processar_texto`. A API consulta o modelo com os fatos e a conversa, retornando `texto`, `tipo_analise` e `resultado`, com `tipo_analise` igual a `conversa`. Após uma resposta bem-sucedida, o Streamlit registra a pergunta e a resposta no histórico e as apresenta na tela.

As seguintes interações foram verificadas na aplicação:

| Interação | Resultado observado |
|---|---|
| Consultar o tempo médio do TJAC em 2025 | 129,6 dias |
| Perguntar qual tribunal havia sido citado anteriormente | TJAC |
| Comparar “esse tribunal” com o TJSE | TJSE com menor tempo: 111,7 dias, contra 129,6 dias do TJAC; diferença de 17,9 dias |

Os valores e a direção da comparação foram conferidos com a base processada. Os exemplos demonstram consulta aos dados e continuidade do contexto entre perguntas, facilitando a interpretação das diferenças entre tribunais.

A validação abrange uma amostra pequena de interações e não garante que todas as respostas do modelo estarão corretas.

## Limitações e decisão sobre a coleta

A base estatística atual contempla somente 2025. O indicador é agregado por tribunal e não representa a duração de processos individuais.
As respostas da IA devem ser conferidas em relação aos dados utilizados.
As fontes atuais permitem coleta por arquivos estruturados, requisições HTTP e Beautiful Soup. Não foi necessário utilizar Selenium.
As fontes e o apoio de IA estão declarados no README.