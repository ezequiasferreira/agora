# Revisão do manuscrito v2 — achados (ART-04)

**Manuscrito:** `Artigo_Agora_Desenvolvimento_Software_v2.docx`
**Revisor:** Gustavo Inácio de Souza (UERR)
**Formato:** cada achado descreve como o texto está e o que recomenda a norma ou o critério indicado. Não há proposta de reescrita.

Normas de referência:
- ABNT NBR 6022:2018: artigo em publicação periódica científica
- ABNT NBR 6023:2018: referências (atualizada em 2025)
- ABNT NBR 10520:2023: citações em documentos
- ABNT NBR 6028:2021: resumo
- IBGE, Normas de apresentação tabular (3. ed., 1993)

---

## 1. Tabelas, quadros e figuras

| ID | Como está | Recomendação | Base |
|---|---|---|---|
| A01 | O artigo tem 3 tabelas (seções 4, 5 e 6.2), sem número, título ou fonte. O texto não faz referência a elas. | Ilustrações e tabelas devem ter identificação (número e título) na parte superior e fonte na parte inferior, e ser citadas no texto. | NBR 6022:2018 (elementos textuais: ilustrações e tabelas); IBGE (1993) |
| A02 | As tabelas das seções 4 (componentes) e 5 (funcionalidades) têm conteúdo textual; a da seção 6.2 tem dados numéricos. Todas são apresentadas do mesmo modo. | Pela convenção brasileira, conteúdo textual organizado em linhas e colunas é apresentado como **quadro**, e dados numéricos como **tabela**. | IBGE (1993); NBR 6022:2018 |
| A03 | Os dois blocos de SQL (6.1 e 6.2) aparecem no corpo do texto sem identificação. | Trechos destacados do texto, como códigos, são tratados como ilustração (por exemplo, "Quadro" ou "Listagem"), com identificação e fonte. | NBR 6022:2018 (ilustrações) |
| A04 | O artigo não tem figuras. | Observação (sem norma aplicável): em relatos de desenvolvimento de software, é usual apresentar ao menos uma figura da arquitetura ou da interface. | Critério de usabilidade do texto |

## 2. Referências e citações

| ID | Como está | Recomendação | Base |
|---|---|---|---|
| A05 | A lista tem 9 referências: 2 artigos científicos (Yu et al., 2018; Pourreza; Rafiei, 2023), 2 documentações técnicas (FastAPI, PostgreSQL), 1 aplicação (Ágora) e 4 documentos internos do projeto. | Observação (sem norma aplicável): a fundamentação acadêmica se apoia em dois trabalhos, o mais recente de 2023. | Critério de fundamentação |
| A06 | Quatro referências são documentos internos (duas anotações de reunião geradas pelo Gemini, "Registros de desenvolvimento" e um registro de ChatGPT), não disponíveis ao leitor. | A referência deve permitir a identificação e a localização do documento pelo leitor. Documentos não acessíveis limitam a verificação das afirmações que se apoiam neles. | NBR 6023:2018 (objetivo e elementos da referência) |
| A07 | A referência "PROJETO ÁGORA. ChatGPT — Acadêmico: acesso a BD de teste acadêmico (1)..." tem, como título, o que parece ser o nome de uma conversa ou de um arquivo, incluindo o sufixo "(1)", e não tem data ("s.d."). | O título deve identificar o documento, e a data é elemento essencial. | NBR 6023:2018 (elementos essenciais) |
| A08 | "s.d." aparece na referência do ChatGPT e na citação "(FASTAPI, s.d.; POSTGRESQL, s.d.)" (seção 2). | Quando a data não consta no documento, a norma indica registrar uma data aproximada entre colchetes (por exemplo, [2026?]), e não "s.d." | NBR 6023:2018 (data); conferir o item na norma |
| A09 | A citação entre parênteses está em caixa alta: "(FASTAPI, s.d.; POSTGRESQL, s.d.)". | Desde 2023, a autoria entre parênteses é grafada em letras maiúsculas e minúsculas; siglas podem permanecer em maiúsculas. | NBR 10520:2023 |
| A10 | A citação usa "POSTGRESQL", mas a referência correspondente começa por "POSTGRESQL GLOBAL DEVELOPMENT GROUP". | A indicação de autoria na citação deve corresponder à entrada da lista de referências. | NBR 10520:2023 |
| A11 | Cinco referências da lista (ÁGORA; as duas anotações do Gemini; "Registros de desenvolvimento"; ChatGPT) não têm citação correspondente no texto. O texto menciona "anotações de reuniões de julho" (3), "registros técnicos" (3.3) e "exemplos históricos em uma base acadêmica" (7) sem indicação de autor e data. | Cada fonte usada no texto deve ser citada no ponto em que é usada, e a lista de referências deve corresponder às obras citadas. | NBR 10520:2023; NBR 6023:2018 |
| A12 | Spider: "Proceedings of EMNLP, 2018", sem local do evento e sem páginas. | O PDF do trabalho indica: Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, p. 3911–3921, Brussels, Belgium, 31 out.–4 nov. 2018, Association for Computational Linguistics. Trabalho apresentado em evento: nome do evento, numeração, ano e local de realização, título do documento (anais/proceedings), dados de publicação e páginas. | NBR 6023:2018 (evento); a versão 2025 detalha os elementos essenciais de evento |
| A13 | DIN-SQL: "NeurIPS, 2023", com link para o arXiv. | A versão no link (arXiv:2304.11015v3, 2 nov. 2023) traz a indicação "37th Conference on Neural Information Processing Systems (NeurIPS 2023)". A referência não informa a versão acessada nem os dados dos anais (título da publicação, volume, páginas). | NBR 6023:2018 (evento; documento on-line) |
| A14 | PostgreSQL: o link aponta para ".../docs/current/...", sem indicação de versão. | Observação (sem norma específica): a página "current" muda a cada versão do PostgreSQL; a data de acesso está indicada, mas a versão do documento não. | Critério de reprodutibilidade |
| A15 | ÁGORA: usa "Observação funcional em: 12 nov. 2026" no lugar de "Acesso em". | Para documentos on-line, o elemento previsto é "Acesso em:". | NBR 6023:2018 (documento on-line) |

## 3. Afirmações e coerência com código e testes

Base adicional: `docs/artigo/README.md` do repositório (regras da equipe: "Distinguir o código da versão em produção, as decisões registradas no histórico e a intenção arquitetural"; "Registra o que foi verificado, o que é somente documentação histórica e o que permanece sem comprovação").

| ID | Seção | Como está | Observado | Recomendação / base |
|---|---|---|---|---|
| A16 | 2 | "O conjunto Spider [...] consolidou a avaliação dessa tarefa com consultas complexas e diferentes esquemas relacionais." | O resumo do trabalho citado sustenta "consultas complexas" e "múltiplos bancos e esquemas" (200 bancos, 138 domínios); apresenta o conjunto como nova tarefa e "desafio forte para pesquisas futuras", sem afirmar consolidação. | Afirmações atribuídas a uma fonte devem corresponder ao conteúdo da fonte (NBR 10520:2023, citação indireta). |
| A17 | 2 | O manuscrito cita o DIN-SQL como fundamento da decomposição da tarefa. | O resumo confirma a decomposição em subproblemas. O mesmo resumo relata avaliação no benchmark BIRD, que o manuscrito não menciona. | Observação, sem norma aplicável. |
| A18 | 3.1 | A seção descreve reuniões de 17/07/2026, assistente com Actions, protótipo com DML/DDL e falhas de túnel. | O conteúdo se apoia apenas em documentos internos (ver A06 e A11), não verificáveis pelo revisor. | Indicar a natureza histórica e não verificada dessas informações (regras da equipe em `docs/artigo/README.md`). |
| A19 | 3.2 | "catálogo automático de PostgreSQL com cinco tabelas, 74 colunas". | O catálogo carregado pelo tradutor (`catalog/data_catalog.json`, lido em `llm/translator.py`; commit ca99ed5) contém 10 objetos (tabelas e views) e 178 colunas. Os valores do texto coincidem com o arquivo `llm/data_catalog.json`. | Informar a data ou a versão a que o número se refere (regras da equipe: distinguir histórico de código atual). |
| A20 | 3.3; 4 (tabela) | "Um trecho de api/app/main.py compartilhado no histórico identifica FastAPI e StaticFiles"; interface descrita como "Página web e JavaScript, conforme histórico". | O repositório público contém esses elementos: `api/app/main.py` (FastAPI, StaticFiles, `/health`, `/ask`) e `frontend/app.js` (`window.location.origin`, linha 1). | Fonte verificável disponível no repositório público (NBR 6023:2018, documento on-line; regras da equipe). |
| A21 | 4.1 | "a existência de um gráfico não identifica, por si só, a biblioteca usada para renderizá-lo." | `frontend/index.html` carrega Chart.js 4.4.7. | Mesma base de A20. |
| A22 | 4 (tabela) | Banco relacional: "o SQL observado usa agora.remuneracoes." | Nos testes de 25/11, o SQL gerado usou também `vw_remuneracoes_semanticas`, `servidores_tlp`, `unidades_tlp` e `fato_remuneracao_rubrica` (matriz EV-06 a EV-12). | Indicar a data e o escopo da observação (regras da equipe). |
| A23 | 4.2 | Lista os controles (só SELECT, instrução única, limite de linhas, timeout, sessão de leitura) como "decisões da implementação documentada", com efetividade "não demonstrada". | Código (commit ca99ed5): validador aceita só SELECT/WITH e instrução única (`api/app/query_validator.py`); `max_rows` = 1.000 e `query_timeout_ms` = 3.000 (`api/app/config.py`); `readonly=True` (`api/app/db.py`). Nos testes, o limite de 1.000 linhas foi observado (EX-01, EX-03). Os demais controles não foram testados. | Indicar o que foi verificado no código, o que foi observado em teste e o que permanece sem comprovação (regras da equipe). |
| A24 | 6.1; 8 | Uma execução da pergunta de janeiro/2025 (1.338); "As consultas realizadas confirmam a operação de um percurso completo." | Em 25/11, a mesma pergunta foi executada 10 vezes: 9 retornaram 1.338 com o SQL do artigo; 1 retornou 9.484, valor que coincide com a contagem de lançamentos de rubricas (matriz EV-01 e EV-12). | Registrar o número de execuções em que o resultado se apoia (critério de aceite da issue #15; regras da equipe). |

## 4. Limitações

**Limitações que o manuscrito já declara:** não é avaliação estatística de acurácia (Resumo, 6, 7); o tempo do painel não é latência total (6.1); custo exibido zero não comprova ausência de custo (6.2); o identificador do modelo é declarado pelo sistema (4.1); os controles de execução não foram demonstrados (4.2); a cobertura de meses além de junho não foi comprovada (6.2); não há avaliação sob concorrência (7).

**Comportamentos observados nos testes e não mencionados no manuscrito:**

| ID | Observado (matriz) | Situação no manuscrito | Base |
|---|---|---|---|
| A25 | A mesma pergunta pode gerar SQL e resultados diferentes entre execuções: EV-01 (9 × 1.338; 1 × 9.484), EV-09 (tabela × view, mesmo resultado), EX-02 (erro e acerto com o mesmo texto). | Não menciona variação entre execuções. | Regras da equipe: registrar o que permanece sem comprovação |
| A26 | Quando a consulta retorna mais de 1.000 linhas, a resposta informa "1.000 registros" (EX-01, EX-03); 1.000 é o valor de `max_rows`. | O limite de linhas é citado (4.2), mas não o seu efeito sobre a resposta. | Idem |
| A27 | O atalho "Evolução mensal" apresentou a resposta em lista, sem tabela e sem gráfico, nas 2 execuções (EV-07). No gráfico de EV-02 (print P2), os rótulos do eixo Y aparecem todos como "1,4". | A tabela da seção 5 descreve o gráfico "para a consulta mensal testada". | Idem |
| A28 | Para "quantas unidades", o SQL contou valores distintos (344), e a tabela tem 369 linhas (EV-10, EV-11); a resposta não informa o critério. Para março/2024, a resposta foi "0 registros", sem mencionar o período coberto pela base (EV-05). | A Introdução trata da preservação da unidade de contagem; o manuscrito não descreve o período nem o volume dos dados. | Idem |
| A29 | Status observados além de ANSWER: NEEDS_CLARIFICATION (EV-03), NOT_ANSWERABLE (EV-04), DB_QUERY_ERROR (EX-02), FORMAT_ERROR (EX-04). | O manuscrito cita apenas o status ANSWER (seção 5). | `docs/contratos.md`, seção 2 |
| A30 | O manuscrito não identifica a versão implantada da aplicação nem o commit do código na data das observações (12/11/2026). | — | Regras da equipe: "Distinguir o código da versão em produção" |
| A31 | A resposta do atalho "Ranking em tabela" exibe nomes e rendimentos de servidores (EV-09). | O manuscrito não trata de dados pessoais nem de aspectos éticos ou de LGPD, embora a base contenha nomes e remunerações. | Regras da equipe: não publicar dados pessoais identificáveis; Lei nº 13.709/2018 (LGPD) |

## 5. Achados da reanálise (26/11/2026)

### 5.1 Elementos pré-textuais

| ID | Como está | Recomendação | Base |
|---|---|---|---|
| A32 | O Resumo é seguido de "Palavras-chave"; o Abstract não é seguido de "Keywords" (o parágrafo seguinte é "1 Introdução"). O Abstract tem 101 palavras e o Resumo, 185. Comparação frase a frase: o Abstract não traz (a) o processo incremental, as responsabilidades dos componentes e as funcionalidades; (b) a data das consultas (12/11/2026); (c) a contextualização do esquema de dados; (d) os indicadores de execução; (e) os três destaques da contribuição (semântica do domínio, mediação do acesso ao banco, apresentação verificável). Onde o Resumo diz que os resultados "demonstram" a operação integrada, o Abstract diz "illustrate". | (1) Pela NBR 6022:2018, o resumo em outro idioma é elemento opcional, mas, quando apresentado, vem acompanhado das palavras-chave em outro idioma, definidas como a versão das palavras-chave na língua do texto para a mesma língua do resumo em língua estrangeira. (2) Pela NBR 6028:2021, item 4.1.7, as palavras-chave figuram logo abaixo do resumo, antecedidas da expressão "Palavras-chave" (no outro idioma, a expressão equivalente, como "Keywords"), seguida de dois-pontos, separadas entre si por ponto e vírgula e finalizadas por ponto. (3) O resumo em outro idioma é a versão do resumo no idioma do documento. Observação: as Palavras-chave em português já seguem a forma do item 4.1.7. | ABNT NBR 6022:2018 (elementos pré-textuais: resumo e palavras-chave em outro idioma); ABNT NBR 6028:2021, item 4.1.7 |
| A33 | A linha de autoria lista dois nomes e termina em vírgula ("Ezequias Carlos Ferreira da Silva, Matheus Vicente Santos Almeida, "), sem vínculo institucional nem contato. | A autoria inclui nome completo, vínculo e contato do(s) autor(es). A definição dos autores cabe à equipe (`docs/artigo/acompanhamento.md`, ponto de atenção 5). | NBR 6022:2018 (autoria) |

### 5.2 Uso dos trabalhos citados

| ID | Seção | Como está | Observado nos trabalhos citados | Base |
|---|---|---|---|---|
| A34 | 2 | "O trabalho DIN-SQL [...] mostra a relevância de decompor a tarefa em subproblemas. Essa referência fundamenta a discussão sobre separação de responsabilidades." | No DIN-SQL, a decomposição ocorre dentro da geração do SQL, em quatro módulos: schema linking, classificação e decomposição, geração do SQL e autocorreção (Pourreza; Rafiei, 2023, seção 4). No Ágora, a separação descrita é entre geração, validação, execução e redação da resposta. As duas decomposições são de naturezas diferentes. | Afirmações atribuídas a uma fonte devem corresponder ao conteúdo da fonte (NBR 10520:2023) |
| A35 | 7 | O manuscrito discute aprendizados sem relacioná-los à taxonomia de erros da literatura citada. | O DIN-SQL classifica falhas de Text-to-SQL; a maior categoria é **schema linking**: falha ao identificar nomes de colunas, tabelas ou entidades da pergunta (seção 3). Comportamentos observados nos testes correspondem a essa definição: coluna inexistente `unidade` em `servidores_tlp` (EX-02) e contagem em `fato_remuneracao_rubrica` para "registros de remuneração" (EV-01/P1). | Observação, sem norma aplicável |
| A36 | 6; 7 | Tempo, tokens e custo são relatados sem referência a valores da literatura. | O DIN-SQL declara, nas limitações (seção 7), custo aproximado de US$ 0,50 e latência aproximada de 60 s por pergunta do Spider com GPT-4. | Observação, sem norma aplicável |
| A37 | 6 | A verificação compara o resultado obtido com o resultado esperado. | O Spider descreve dois critérios complementares: correspondência exata do SQL, que pode gerar falsos negativos, e acurácia de execução, que pode gerar falsos positivos quando SQLs diferentes retornam o mesmo resultado (Yu et al., 2018, seção 6). Nos testes, EV-09 retornou o mesmo resultado com SQLs diferentes (tabela × view). | Observação, sem norma aplicável |

### 5.3 Código e aplicação publicada (commit ca99ed5; sem alterações de código nos commits posteriores até 24/11/2026)

| ID | Seção | Como está | Observado | Base |
|---|---|---|---|---|
| A38 | 3.3 | Cita as chamadas a `/ask` e `/health`. | A especificação publicada da API (`/openapi.json`, consultada em 26/11/2026) lista também `POST /query`, que recebe SQL diretamente; no código, esse endpoint passa pelo mesmo validador e pela sessão somente leitura, sem autenticação no código (`api/app/main.py`). Versão declarada pela API publicada: 0.3.0, a mesma do código. | Regras da equipe (`docs/artigo/README.md`); tema da issue #14 (ART-03) |
| A39 | 4.2 | O limite de linhas é citado como controle. | `api/app/db.py` lê no máximo `max_rows` (1.000) linhas, e `api/app/ask_service.py` envia à etapa de resposta `row_count = len(linhas)`, sem indicação de que o resultado foi limitado. Isso é compatível com as respostas "1.000 registros" de EX-01 e EX-03. | Regras da equipe |
| A40 | 4.2; 7 | — | O código não tem nova tentativa ou autocorreção após `DB_QUERY_ERROR` ou `FORMAT_ERROR`: a resposta de erro é devolvida ao usuário (EX-02, EX-04). O DIN-SQL descreve um módulo de autocorreção (Pourreza; Rafiei, 2023, seção 4.4). | Observação |
| A41 | 4.2 | Controles descritos como "decisões da implementação documentada", com efetividade "não demonstrada". | O validador do repositório foi executado em ambiente isolado em 26/11/2026 com 13 instruções: aceitou SELECT e CTE de leitura (inclusive com palavras proibidas dentro de texto ou comentário) e bloqueou DELETE, UPDATE, INSERT, DROP, TRUNCATE, SELECT INTO, CTE com DELETE e duas instruções (`evidencias/validador_sql_ca99ed5.txt`). Execução sobre o código, não sobre a aplicação publicada. | Regras da equipe |
| A42 | 5 | Tabela da seção 5: "Gráfico da resposta: visualização de evolução para a consulta mensal testada." | O gráfico é montado a partir da tabela redigida na resposta (`frontend/app.js`). A função que lê os números (`converterNumeroTexto`) trata o ponto como separador decimal quando não há vírgula: "1.338" vira 1,338. Executada em 26/11/2026 sobre os valores de EV-02, a função retornou 1,338; 1,379; 1,347 (valores com vírgula, como "R$ 21.825.225,94", foram lidos corretamente). Isso é compatível com o print P2, em que o eixo Y exibe "1,4". Em nova execução, em 27/11/2026, a dica do ponto de fevereiro exibiu "Quantidade de registros: 1,38" para o valor 1.379 da tabela (print P6). | Observação |
| A43 | 3.2 | O texto atribui à camada semântica o papel de orientar a escolha de tabelas e relações. | O glossário (`semantic/profiles/tjrr/glossary.json`) indica `fato_remuneracao_rubrica` quando a pergunta trata diretamente de lançamentos detalhados da folha. Na execução P1, a pergunta sobre "registros de remuneração" retornou 9.484, valor que coincide com a contagem dessa tabela (EV-12). | Observação |

## 6. Verificações sem divergência

Afirmações do manuscrito conferidas sem divergência; registradas para documentar o alcance da revisão.

| ID | Seção | Afirmação | Conferência |
|---|---|---|---|
| V01 | 6.2 | Seis linhas, jan–jun/2025 | A soma das seis linhas (1.338 + 1.379 + 1.348 + 1.357 + 1.355 + 1.347) é 8.124, igual ao total de registros de remuneração informado no README ("Base atual do MVP"). |
| V02 | 6.1; 6.2; 7 | Tokens por etapa e proporção da geração de SQL | 18.844 + 818 = 19.662; 18.881 + 1.008 = 19.889; 18.881 ÷ 19.889 = 94,93% (o texto diz "aproximadamente 94,9%"). |
| V03 | 3.3 | Frontend usa `window.location.origin` | `frontend/app.js`, linha 1. |
| V04 | 3.3; 4 | FastAPI com StaticFiles; `/ask` e `/health` | `api/app/main.py`. |
| V05 | 3.2 | Domínio: remunerações, lotações, unidades, cargos, funções e rubricas | Tabelas correspondentes em `database/ddl/estrutura_agora.sql`. |
| V06 | Resumo | Extensão e palavras-chave | Resumo com 185 palavras; palavras-chave antecedidas de "Palavras-chave:", separadas por ponto e vírgula e finalizadas por ponto (NBR 6028:2021, item 4.1.7). |
| V07 | 2 | Spider: consultas complexas sobre esquemas diferentes; DIN-SQL: decomposição em subproblemas | Resumos e seções 3–4 dos trabalhos (PDFs consultados em 26/11/2026). |
| V08 | 5 | Interface e funcionalidades descritas | Matriz EV-I01 a EV-I09. |
| V09 | 6.2 | "6 registros" refere-se às seis linhas agregadas | Print P2 ("6 registros" acima da tabela de seis meses). |
| V10 | 6.1 | O tempo do painel não é a latência total | Matriz EV-09: 3 ms no painel × 10,94 s cronometrados. |
