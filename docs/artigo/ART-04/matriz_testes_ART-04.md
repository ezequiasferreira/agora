# Matriz de testes e evidências — Ágora (ART-04, issue #15)

**Responsável:** Gustavo Inácio de Souza (UERR)
**Ambiente:** navegador Brave, Windows 11 · aplicação https://agora.grupolealferreira.com.br/
**Datas:** 24/11/2026 (exploração), 25/11/2026 (execução) e 26/11/2026 (revisão de código e um teste exploratório)
**Versão:** a API publicada declara a versão 0.3.0 (`/openapi.json`, 26/11/2026). Código de referência: commit `ca99ed5` (20/08/2026), também 0.3.0, sem alterações de código até 24/11/2026. A versão declarada coincide, mas a identidade entre o código implantado e esse commit não foi verificada.
**Manuscrito de referência:** `Artigo_Agora_Desenvolvimento_Software_v2.docx` (observações de 12/11/2026)
**Formato:** segue `docs/artigo/modelo_evidencias.md`. Situação: aprovado | reprovado | inconclusivo | não executado.
**Evidências:** `evidencias/paineis_texto_bruto.md` (texto de cada painel), prints P1–P5 e `evidencias/validador_sql_ca99ed5.txt`.

> Execuções isoladas, registradas uma a uma. Nenhum valor desta matriz é média ou taxa, e esta verificação não é avaliação estatística de acurácia.

---

## 1. Matriz resumida

| ID | Pergunta/objetivo | Esperado (fundamento) | Obtido | SQL verificado? | Situação | Evidência |
|---|---|---|---|---|---|---|
| EV-01 | Contagem de janeiro/2025 | 1.338, conforme observação histórica do manuscrito (6.1) | 10 execuções: 9 retornaram 1.338 com o SQL do manuscrito; 1 (P1) retornou 9.484 | Sim nas 9; não capturado em P1 | Aprovado em 9 de 10 execuções; reprovado em 1 (P1) | X1, R1–R7, ~10h15, P1 |
| EV-02 | Agrupamento mensal em 2025 | Seis linhas jan–jun, com os valores e o gráfico do manuscrito (6.2) | 2 execuções com os 6 valores e o gráfico "Evolução — Quantidade de registros"; soma 8.124, igual ao total do README | Sim (igual ao do manuscrito) | Aprovado | T02, P2, P6 |
| EV-03 | Pergunta ambígua | Solicitação de esclarecimento (`docs/contratos.md`, seção 2) | NEEDS_CLARIFICATION nas 2 perguntas, sem SQL | Não se aplica (sem SQL) | Aprovado | T09a, T09b |
| EV-04 | Informação não disponível | Indicação de não respondível (`docs/contratos.md`, seção 2) | NOT_ANSWERABLE nas 2 execuções, sem SQL | Não se aplica | Aprovado | T10, P3 |
| EV-05 | Período fora da base (março/2024) | Não apresentar valor inexistente na base (README: base jan–jun/2025) | 0 registros, status ANSWER, nas 2 execuções | Sim | Aprovado | T11, P4 |
| EV-06 | Filtro/agrupamento diferente: rendimento líquido por mês | Tabela mensal com gráfico (manuscrito, seção 5) | 2 execuções com 6 linhas e gráfico; títulos do gráfico diferentes entre as execuções | Sim (view `vw_remuneracoes_semanticas`) | Aprovado | E3, E3b |
| EV-07 | Atalho "Evolução mensal" | Valores mensais jan–jun (texto do atalho; o manuscrito não descreve o formato) | 2 execuções com os mesmos valores de EV-06, em lista, sem tabela e sem gráfico | Sim (tabela `remuneracoes`) | Aprovado (valores); formato registrado como observação | X4, ~10h15 |
| EV-08 | Atalho "Servidores por unidade judiciária" | Resposta com SQL coerente com a pergunta (manuscrito 5.2) | 545 em 4 execuções | Sim | Aprovado | E1, X2, ~10h09, ~10h15 |
| EV-09 | Atalho "Ranking em tabela" | 10 linhas com servidor, cargo, lotação e rendimento líquido (texto do atalho; o manuscrito 5.1 registra que não verificou) | 3 execuções com as mesmas 10 linhas; SQL sobre a tabela numa e sobre a view noutra; latência total de 10,94 s (T15) | Sim (2 de 3) | Aprovado | T15, P5, ~10h15 |
| EV-10 | "Quantas unidades existem?" | 369 unidades (README, "Base atual do MVP") | 344 em 2 execuções (`COUNT(DISTINCT unidade)`) | Sim | Inconclusivo: a pergunta admite dois critérios de contagem (ver EV-11) | E2, T07 |
| EV-11 | Linhas da tabela de unidades | 369 (README) | 369 (`COUNT(*)`) | Sim | Aprovado | T08 |
| EV-12 | Origem do valor 9.484 (diagnóstico) | — | 9.484 lançamentos em `fato_remuneracao_rubrica` em jan/2025 | Sim | Não se aplica (diagnóstico) | T16 |
| EV-13 | `/health` | Resposta de disponibilidade (manuscrito 3.3) | `{"status":"ok","database":"ok"}` | Não se aplica | Aprovado | T14 |

## 2. Interface (manuscrito, seção 5)

| ID | Verificação | Esperado (fundamento) | Obtido | Situação |
|---|---|---|---|---|
| EV-I01 | Título | "Converse com os dados da organização" (5) | Igual | Aprovado |
| EV-I02 | Campo e botão | Campo de pergunta e botão "Perguntar" (5) | Presentes | Aprovado |
| EV-I03 | Envio por Enter | Indicação de envio pela tecla Enter (5) | Enviado com Enter | Aprovado |
| EV-I04 | Botão durante a execução | "Processando..." (5) | "Processando..." | Aprovado |
| EV-I05 | Área de resposta durante a execução | Informa que os dados estão sendo consultados (5) | "Consultando os dados..." | Aprovado |
| EV-I06 | Indicador de disponibilidade | Indicador presente (tabela da 5) | "Sistema disponível"; durante a execução, "Verificando sistema..." | Aprovado |
| EV-I07 | Atalhos de exemplo | Quatro temas (tabela da 5) | Quatro atalhos | Aprovado |
| EV-I08 | Clique em atalho | Preenche o campo; envio é ação posterior (tabela da 5) | Preenche, não envia | Aprovado |
| EV-I09 | "Detalhes técnicos" | Área recolhível (5.2) | Abre e fecha pelo título; o estado se mantém entre perguntas | Aprovado |

## 3. Registros exploratórios (sem resultado esperado prévio)

| ID | Pergunta | Obtido | SQL | Evidência |
|---|---|---|---|---|
| EX-01 | Registros de remuneração em janeiro | "Foram retornados 1.000 registros"; 207.750 tokens, 188.861 na resposta final | `SELECT *` na view, `mes = 1`, sem filtro de ano | D1 |
| EX-02 | Servidores por unidade judiciária (2 envios do mesmo texto) | 1º: DB_QUERY_ERROR; 2º: 131 unidades com contagem | 1º: `GROUP BY unidade` em `servidores_tlp`, coluna inexistente na tabela; 2º: não capturado | D2, D5 |
| EX-03 | Ranking em tabela da remuneração em janeiro dos servidores por unidade judiciária | "contém 1.000 registros", 20 exibidos; 68.398 tokens | `ROW_NUMBER()` na view, sem `LIMIT` | D3 |
| EX-04 | quantas tabelas e quantas colunas existem? | FORMAT_ERROR: "A LLM retornou QUERY sem uma instrução SQL." | nenhum | T17 |

Excluídos: D4, D6 e D7 (texto da pergunta não registrado). Observação do testador: em 25/11, variações de perguntas com menos detalhes retornaram NEEDS_CLARIFICATION com frequência (textos não registrados).

## 4. Revisão de código (commit ca99ed5)

| ID | Objetivo | Obtido | Fonte |
|---|---|---|---|
| RC-01 | Validador de SQL (manuscrito 4.2) | 13 instruções executadas: SELECT e CTE de leitura aceitos; DELETE, UPDATE, INSERT, DROP, TRUNCATE, SELECT INTO, CTE com DELETE e duas instruções bloqueados | `api/app/query_validator.py`; `evidencias/validador_sql_ca99ed5.txt` |
| RC-02 | Limites de execução (4.2) | `max_rows` = 1.000; `query_timeout_ms` = 3.000; sessão `readonly=True` | `api/app/config.py`; `api/app/db.py` |
| RC-03 | Contagem de linhas enviada à resposta | `row_count = len(linhas)` após leitura limitada a `max_rows`, sem indicador de limitação | `api/app/db.py`; `api/app/ask_service.py` |
| RC-04 | Catálogo (3.2) | Catálogo carregado: 10 objetos, 178 colunas; `llm/data_catalog.json`: 5 tabelas, 74 colunas | `catalog/data_catalog.json`; `llm/translator.py` |
| RC-05 | Biblioteca do gráfico (4.1) | Chart.js 4.4.7 | `frontend/index.html` |
| RC-06 | Endpoints | `GET /health`, `POST /ask`, `POST /query` (SQL direto, validado, sem autenticação no código); confirmados em `/openapi.json` publicado | `api/app/main.py` |
| RC-07 | Tratamento de erro | Sem nova tentativa ou autocorreção após `DB_QUERY_ERROR` ou `FORMAT_ERROR` | `api/app/ask_service.py` |

---

## 5. Fichas (modelo `docs/artigo/modelo_evidencias.md`)

### EV-01 — Contagem de janeiro/2025
- **Responsável:** Gustavo Inácio de Souza · **Data e horário:** 25/11/2026, ~09h27 a ~10h15 · **Ambiente / versão / commit:** Brave, Windows 11; API 0.3.0; código de referência ca99ed5 · **Issue:** #15 · **Tipo:** teste funcional
- **Objetivo:** reproduzir a seção 6.1 do manuscrito
- **Pergunta:** "Quantos registros de remuneração existem em janeiro de 2025?" (atalho "Registros de remuneração em janeiro")
- **Resultado esperado e fundamento:** 1.338; `COUNT(*)` em `agora.remuneracoes` com `ano = 2025 AND mes = 1` (manuscrito 6.1)
- **Estado da LLM:** ANSWER (10 de 10)
- **SQL gerado:** igual ao do manuscrito nas 9 execuções com painel copiado; não capturado em P1
- **Resposta efetiva:** 1.338 em 9 execuções; "9.484 registros de remuneração" em 1 (P1)
- **Formato:** texto
- **Tempo SQL:** 0–2 ms nas 9; 1.781 ms em P1 · **Latência ponta a ponta:** não medida · **Tokens:** 19.578–19.659 nas 9
- **Resultado:** aprovado em 9 de 10 execuções; reprovado em 1
- **Evidência:** `paineis_texto_bruto.md` (X1, R1–R7, ~10h15); `P1_jan2025_9484.png`
- **Limitações:** o SQL de P1 não foi capturado; a execução se sustenta na pergunta visível no campo do print e na redação da resposta, que repete os termos da pergunta. O valor 9.484 coincide com a contagem de lançamentos de rubricas em jan/2025 (EV-12), mas a causa não foi verificada.

### EV-02 — Agrupamento mensal em 2025
- **Data e horário:** 25/11/2026, ~09h35 e ~09h50 · **Ambiente / versão / commit:** como EV-01 · **Tipo:** teste funcional
- **Pergunta:** "Gere uma TABELA com a quantidade de registros de remuneração por mês de 2025, ordenada por mês"
- **Resultado esperado:** jan 1.338 · fev 1.379 · mar 1.348 · abr 1.357 · mai 1.355 · jun 1.347; gráfico "Evolução — Quantidade de registros" (manuscrito 6.2)
- **Estado da LLM:** ANSWER · **SQL:** `SELECT mes, COUNT(*) AS quantidade_registros FROM agora.remuneracoes WHERE ano = 2025 GROUP BY mes ORDER BY mes` (igual ao do manuscrito)
- **Resposta efetiva:** os 6 valores esperados; janeiro igual a EV-01 · **Formato:** texto, tabela e gráfico
- **Tempo SQL:** 3 ms · **Latência:** não medida · **Tokens:** 19.846 (geração 18.838; resposta 1.008)
- **Resultado:** aprovado
- **Evidência:** `paineis_texto_bruto.md` (T02); `P2_tabela_mensal.png`
- **Observações:** no print P2, os rótulos do eixo Y aparecem todos como "1,4". Em nova execução, em 27/11/2026 (~09h10), a dica do ponto de fevereiro exibiu "Quantidade de registros: 1,38" para o valor 1.379 da tabela (`P6_grafico_tooltip_fevereiro.png`; ver achado A42).

### EV-03 — Pergunta ambígua
- **Data e horário:** 25/11/2026, ~10h36 · **Tipo:** teste funcional
- **Perguntas:** "Ranking da remuneração por unidade em janeiro"; "Qual foi o maior valor?"
- **Resultado esperado:** NEEDS_CLARIFICATION (`docs/contratos.md`, seção 2)
- **Estado da LLM:** NEEDS_CLARIFICATION nas duas · **SQL:** nenhum
- **Resposta efetiva:** pedidos de ano e medida; de informação, período ou categoria · **Tokens:** 18.890; 18.724
- **Resultado:** aprovado · **Evidência:** `paineis_texto_bruto.md` (T09a, T09b)
- **Limitações:** o texto das perguntas não aparece na cópia (campo limpo após o envio); as perguntas foram sugeridas na conversa e confirmadas pelo testador.

### EV-04 — Informação não disponível
- **Data e horário:** 25/11/2026, ~09h36 e ~09h50 · **Tipo:** teste funcional
- **Pergunta:** "Quantos processos judiciais foram julgados em 2025?"
- **Resultado esperado:** NOT_ANSWERABLE (`docs/contratos.md`, seção 2)
- **Estado da LLM:** NOT_ANSWERABLE (2 de 2) · **SQL:** nenhum · **Tokens:** 18.726; 18.680
- **Resultado:** aprovado · **Evidência:** `paineis_texto_bruto.md` (T10); `P3_processos_judiciais.png`

### EV-05 — Período fora da base
- **Data e horário:** 25/11/2026, ~09h36 e ~09h50 · **Tipo:** teste funcional
- **Pergunta:** "Quantos registros de remuneração existem em março de 2024?"
- **Resultado esperado:** não apresentar valor inexistente na base (README: base jan–jun/2025)
- **Estado da LLM:** ANSWER · **SQL:** `SELECT COUNT(*) AS quantidade_registros FROM agora.remuneracoes WHERE ano = 2024 AND mes = 3`
- **Resposta efetiva:** 0 registros (2 de 2) · **Tempo SQL:** 0 ms · **Tokens:** 19.676; 19.641
- **Resultado:** aprovado · **Evidência:** `paineis_texto_bruto.md` (T11); `P4_marco_2024.png`
- **Observações:** a resposta não menciona o período coberto pela base.

## 6. Checagem de conformidade (modelo da equipe)

- [x] O dado veio de execução ou de fonte técnica identificável (painéis copiados, prints, código com commit)
- [x] Data, ambiente e versão foram informados (versão declarada pela API; identidade com o commit não verificada)
- [x] Não foram expostos dados pessoais ou segredos (nomes omitidos nos textos; P5 usado na versão pixelada)
- [x] O SQL corresponde à pergunta e à unidade de contagem desejada (exceções registradas: EV-01/P1, EV-10, EX-01 a EX-03)
- [x] Não foi afirmada média de desempenho com base em uma única medição (latência medida uma vez: 10,94 s, EV-09); percepção do testador, sem cronômetro, de tempo semelhante (~10 s) nas demais execuções, registrada como observação
- [x] Eventuais limitações e inconclusões foram registradas
