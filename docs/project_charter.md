# Project Charter — TP5 Juizados Especiais

**Autora:** Carolina Gabriela Mesquita

## Problema

Os dados públicos do CNJ permitem comparar o tempo médio até a sentença nos Juizados Especiais. O projeto organiza esses indicadores para facilitar a compreensão das diferenças entre os tribunais.

A base utilizada reúne dados de 2025 dos 27 Tribunais de Justiça. Na etapa 5, esses dados foram integrados a um painel interativo com consultas, comparações e memória conversacional, permitindo perguntas encadeadas sobre os tribunais.

**Pergunta do projeto:** como comparar e compreender as diferenças no tempo médio até a sentença nos Juizados Especiais dos 27 Tribunais de Justiça, utilizando os dados de 2025?

**Objetivo:** permitir que o usuário consulte os indicadores, visualize comparações e obtenha explicações apoiadas por IA no mesmo painel.

**Relação com a ODS 16:** facilitar a compreensão de dados públicos da Justiça, contribuindo para uma leitura transparente dos indicadores associados às instituições.

## Escopo

O projeto utiliza dados de 2025 dos 27 Tribunais de Justiça para apresentar consultas e comparações sobre o tempo médio até a sentença nos Juizados Especiais. As notícias permanecem como informações de contexto, e as observações complementares são armazenadas separadamente da base oficial.

Como ponto de partida, a fase 4 integrou o TinyLlama ao FastAPI para produzir explicações textuais sobre comparações fornecidas na entrada.

Na etapa 5, foi implementada memória conversacional na página de comparação entre tribunais. O histórico fica na sessão do Streamlit e é reenviado à API junto com cada nova pergunta, permitindo retomar informações de interações anteriores.

O modelo utilizado é nvidia/nemotron-3.5-lightning:free, acessado pela API do OpenRouter com ChatOpenAI. A escolha ocorreu após os testes com o TinyLlama apresentarem falhas na recuperação do contexto da conversa.

O prompt recebe os fatos da base estatística e orienta o modelo a responder em português, utilizar somente os dados fornecidos, preservar as siglas e produzir uma frase curta. Quando faltar informação para compreender a pergunta, a orientação é pedir esclarecimento.

A engenharia de prompts será utilizada para orientar a tarefa, o formato da resposta e o uso dos dados fornecidos.

## Objetivos e critérios de sucesso

- apresentar os dados dos 27 tribunais referentes a 2025;
- permitir consultas, filtros, comparações, tabelas, gráficos e download;
- manter o contexto entre perguntas sobre os tribunais por meio de memória conversacional;
- permitir a interação do usuário com essa funcionalidade no dashboard;
- preservar siglas, valores e direção das comparações nos exemplos de validação;
- manter o recebimento e a persistência das observações complementares;
- documentar o caminho dos dados, desde a coleta e preparação até os resultados apresentados com apoio de IA.


## Público e ODS

O público desta aplicação acadêmica é formado por alunos e professores interessados em consultar e comparar dados públicos dos Juizados Especiais.
O projeto está relacionado à ODS 16, pela proposta de facilitar a compreensão de indicadores da Justiça e a leitura transparente de dados institucionais.


## Riscos

O modelo pode produzir informações incorretas. Por isso, suas respostas devem ser conferidas em relação aos dados utilizados.

A base estatística atual contempla somente 2025, mas mantive para minimizar os erros do modelo. 

O modelo por API apresentou respostas corretas nos testes de consulta, recuperação do tribunal anterior e comparação contextual. Esses testes abrangem poucos exemplos e não garantem que todas as respostas estarão corretas.

O uso do modelo depende da disponibilidade da API e da chave configurada no ambiente do servidor. As fontes e o apoio de IA estão declarados no README.