# Painéis registrados — texto bruto (ART-04)

Texto dos painéis "Detalhes técnicos" e das respostas, conforme copiado da aplicação pelo testador (Gustavo Inácio de Souza) durante as execuções e colado na conversa de trabalho. Navegador Brave, Windows 11. Aplicação: https://agora.grupolealferreira.com.br/

**Edição aplicada:** nomes de pessoas e de unidades nominais foram omitidos ([omitido]); o restante foi mantido como copiado. As listas longas foram resumidas e marcadas como tal.

**Origem da pergunta** (o campo de pergunta é limpo após o envio, então nem toda cópia o mostra):
- **[campo]**: pergunta visível no campo, na cópia ou no print;
- **[atalho]**: atalho clicado; o texto vem do atalho em `frontend/index.html`;
- **[declarada]**: informada pelo testador na conversa;
- **[sugerida+eco]**: pergunta sugerida na conversa e executada pelo testador; a resposta repete os termos da pergunta.

---

## 24/11/2026 (exploração)

### E1 — [sugerida+eco] (atalho "Servidores por unidade judiciária" sugerido) · ~11h20
Resposta: "545 servidores pertencem às unidades judiciárias de primeiro e segundo graus."
Status ANSWER · Tempo da consulta 127 ms · Modelo gpt-5.6-luna · Tokens totais 19.660 · Entrada 19.434 · Cache 0 · Saída 226 · Custo US$ 0.00000000
```
SELECT COUNT(DISTINCT matricula) AS quantidade_servidores
FROM agora.servidores_tlp
WHERE categoria_tlp = 'UNIDADES JUDICIÁRIAS DE PRIMEIRO E SEGUNDO GRAUS'
```
Geração do SQL: Entrada 18.643 · Cache 0 · Saída 199 · Total 18.842 | Resposta final: Entrada 791 · Cache 0 · Saída 27 · Total 818

### E2 — "Quantas unidades existem?" [sugerida+eco] · ~11h20
Resposta: "Existem 344 unidades."
Status ANSWER · 14 ms · Tokens totais 19.643 · Entrada 19.411 · Cache 0 · Saída 232 · Custo US$ 0.00000000
```
SELECT COUNT(DISTINCT unidade) AS quantidade_unidades
FROM agora.unidades_tlp
WHERE unidade IS NOT NULL
```
Geração do SQL: 18.632 · 0 · 214 · 18.846 | Resposta final: 779 · 0 · 18 · 797

### E3 — "Gere uma tabela com o total de rendimento líquido pago por mês em 2025, ordenada por mês." [sugerida+eco] · ~11h33
Resposta: "Total de rendimento líquido pago por mês em 2025:" · 6 registros · Janeiro R$ 21.825.225,94 · Fevereiro R$ 24.255.192,24 · Março R$ 29.047.631,80 · Abril R$ 18.303.110,36 · Maio R$ 21.065.661,06 · Junho R$ 23.610.157,39 · VISUALIZAÇÃO "Evolução — Total pago", 6 períodos
Status ANSWER · 98 ms · Tokens totais 20.000 · Entrada 19.538 · Cache 0 · Saída 462 · Custo US$ 0.00000000
```
SELECT
    ano,
    mes,
    SUM(COALESCE(rendimento_liquido, 0)) AS total_rendimento_liquido_pago
FROM agora.vw_remuneracoes_semanticas
WHERE ano = 2025
GROUP BY ano, mes
ORDER BY mes
```
Geração do SQL: 18.650 · 0 · 224 · 18.874 | Resposta final: 888 · 0 · 238 · 1.126

---

## 25/11/2026

### E3b — "Gere uma tabela com o total de rendimento líquido pago por mês em 2025, ordenada por mês." [campo] · ~09h01
Resposta: mesmos 6 valores de E3; tabela "Mês | Total de rendimento líquido pago"; VISUALIZAÇÃO "Evolução — Total de rendimento líquido pago", 6 períodos. Painel não copiado.
Durante a execução: botão "Processando..."; área de resposta "Consultando os dados..."; indicador "Verificando sistema...".

### D1 — "Registros de remuneração em janeiro" [declarada] · ~09h18
Resposta: "Foram retornados 1.000 registros individuais de remuneração referentes a janeiro de 2025, associados a várias pessoas, incluindo [omitido]."
Status ANSWER · 169 ms · Tokens totais 207.750 · Entrada 207.190 · Cache 0 · Saída 560 · Custo US$ 0.00000000
```
SELECT *
FROM agora.vw_remuneracoes_semanticas
WHERE mes = 1
ORDER BY ano, id
```
Geração do SQL: 18.635 · 0 · 254 · 18.889 | Resposta final: 188.555 · 0 · 306 · 188.861

### D2 — "Servidores por unidade judiciária" [declarada] · ~09h18
Resposta: "Não foi possível executar a consulta nos dados."
Status DB_QUERY_ERROR · Tempo — · Tokens totais 18.953 · Entrada 18.635 · Cache 0 · Saída 318
```
SELECT unidade, COUNT(DISTINCT matricula) AS quantidade_servidores FROM agora.servidores_tlp WHERE categoria_tlp = 'UNIDADES JUDICIÁRIAS DE PRIMEIRO E SEGUNDO GRAUS' GROUP BY unidade ORDER BY unidade
```
Geração do SQL: 18.635 · 0 · 318 · 18.953 | Resposta final: 0 · 0 · 0 · 0

### D3 — "Ranking em tabela da remuneração em janeiro dos servidores por unidade judiciária" [campo] · ~09h18
Resposta: "O ranking da remuneração em janeiro contém 1.000 registros. As 20 primeiras posições são:" · 20 registros (Ranking, Servidor, Unidade judiciária, Remuneração) · nomes [omitido]
Status ANSWER · 34 ms · Tokens totais 68.398 · Entrada 66.521 · Cache 0 · Saída 1.877
```
SELECT
    ROW_NUMBER() OVER (ORDER BY rendimento_liquido DESC NULLS LAST, nome) AS ranking,
    nome AS servidor,
    lotacao_canonica AS unidade_judiciaria,
    rendimento_liquido AS remuneracao
FROM agora.vw_remuneracoes_semanticas
WHERE ano = 2025
  AND mes = 1
ORDER BY rendimento_liquido DESC NULLS LAST, nome
```
Geração do SQL: 18.643 · 0 · 670 · 19.313 | Resposta final: 47.878 · 0 · 1.207 · 49.085

### D5 — "Servidores por unidade judiciária" [campo] · ~09h27
Resposta: "Foram identificados servidores em 131 unidades judiciárias:" · 131 registros (Unidade judiciária | Quantidade de servidores) · lista resumida: 131 linhas com nomes de unidades [omitido]. Painel não copiado.

### X1 — atalho "Registros de remuneração em janeiro" [atalho] · ~09h27
Resposta: "Existem 1.338 registros de remuneração em janeiro de 2025."
Status ANSWER · 2 ms · Tokens totais 19.609 · Entrada 19.430 · Cache 0 · Saída 179
```
SELECT COUNT(*) AS quantidade_registros FROM agora.remuneracoes WHERE ano = 2025 AND mes = 1
```
Geração do SQL: 18.641 · 0 · 150 · 18.791 | Resposta final: 789 · 0 · 29 · 818

### X2 — atalho "Servidores por unidade judiciária" [atalho] · ~09h27
Resposta: "Há 545 servidores pertencentes às unidades judiciárias de primeiro e segundo graus."
Status ANSWER · 1 ms · Tokens totais 19.741 · Entrada 19.434 · Cache 0 · Saída 307
```
SELECT COUNT(DISTINCT matricula) AS quantidade_servidores
FROM agora.servidores_tlp
WHERE categoria_tlp = 'UNIDADES JUDICIÁRIAS DE PRIMEIRO E SEGUNDO GRAUS'
```
Geração do SQL: 18.643 · 0 · 278 · 18.921 | Resposta final: 791 · 0 · 29 · 820

### X3 — atalho "Ranking em tabela" [campo] · ~09h27
Resposta: "As 10 maiores remunerações líquidas de junho de 2025 foram:" · 10 registros (#, Servidor, Cargo, Lotação, Rendimento líquido) · nomes [omitido]. Painel não copiado (ver T15).

### X4 — atalho "Evolução mensal" [atalho] · ~09h27
Resposta: "Evolução do rendimento líquido total de janeiro a junho de 2025:" · Janeiro: R$ 21.825.225,94 · Fevereiro: R$ 24.255.192,24 · Março: R$ 29.047.631,80 · Abril: R$ 18.303.110,36 · Maio: R$ 21.065.661,06 · Junho: R$ 23.610.157,39 (em lista, sem tabela e sem visualização)
Status ANSWER · 8 ms · Tokens totais 19.947 · Entrada 19.525 · Cache 0 · Saída 422
```
SELECT ano, mes, SUM(COALESCE(rendimento_liquido, 0)) AS rendimento_liquido_total FROM agora.remuneracoes WHERE ano = 2025 AND mes BETWEEN 1 AND 6 GROUP BY ano, mes ORDER BY ano, mes
```
Geração do SQL: 18.644 · 0 · 215 · 18.859 | Resposta final: 881 · 0 · 207 · 1.088

### D6 — [pergunta não registrada] · ~09h27 · excluído da matriz
Resposta: "A consulta retornou 1.000 registros de remuneração referentes a janeiro de 2025 [...]" · ANSWER · 19 ms · 207.873 tokens · cache 18.632 · `SELECT * FROM agora.vw_remuneracoes_semanticas WHERE ano = 2025 AND mes = 1 ORDER BY nome`

### D4 e D7 — [pergunta não registrada] · ~09h18 e ~09h27 · excluídos da matriz
D4: NEEDS_CLARIFICATION · 18.856 tokens · pediu a medida de remuneração e se seriam todas as unidades ou as maiores.
D7: NEEDS_CLARIFICATION · 18.956 tokens · cache 18.640 · pediu o ano de janeiro e a medida do ranking.

### T02 — "Gere uma TABELA com a quantidade de registros de remuneração por mês de 2025, ordenada por mês" [campo] · ~09h35
Resposta: "Quantidade de registros de remuneração por mês de 2025:" · 6 registros · Janeiro 1.338 · Fevereiro 1.379 · Março 1.348 · Abril 1.357 · Maio 1.355 · Junho 1.347 · VISUALIZAÇÃO "Evolução — Quantidade de registros", 6 períodos
Status ANSWER · 3 ms · Tokens totais 19.846 · Entrada 19.495 · Cache 0 · Saída 351
```
SELECT mes, COUNT(*) AS quantidade_registros
FROM agora.remuneracoes
WHERE ano = 2025
GROUP BY mes
ORDER BY mes
```
Geração do SQL: 18.653 · 0 · 185 · 18.838 | Resposta final: 842 · 0 · 166 · 1.008

### T10 — "Quantos processos judiciais foram julgados em 2025?" [sugerida+eco] · ~09h36
Resposta: "Informação não disponível nos dados. Os dados disponíveis não possuem informações sobre processos judiciais nem sobre julgamento em 2025."
Status NOT_ANSWERABLE · Tempo — · Tokens totais 18.726 · Entrada 18.640 · Cache 0 · Saída 86 · SQL —
Geração do SQL: 18.640 · 0 · 86 · 18.726 | Resposta final: 0 · 0 · 0 · 0

### T11 — "Quantos registros de remuneração existem em março de 2024?" [sugerida+eco] · ~09h36
Resposta: "Em março de 2024, foram identificados 0 registros de remuneração."
Status ANSWER · 0 ms · Tokens totais 19.676 · Entrada 19.429 · Cache 0 · Saída 247
```
SELECT COUNT(*) AS quantidade_registros FROM agora.remuneracoes WHERE ano = 2024 AND mes = 3
```
Geração do SQL: 18.641 · 0 · 218 · 18.859 | Resposta final: 788 · 0 · 29 · 817

### T15 — atalho "Ranking em tabela": "Gere uma TABELA com as 10 maiores remunerações líquidas de junho de 2025, mostrando servidor, cargo, lotação e rendimento líquido." [campo] · ~09h40
Resposta: "As 10 maiores remunerações líquidas de junho de 2025 foram:" · 10 registros (Servidor, Cargo, Lotação, Rendimento líquido) · nomes e lotações [omitido] · maior valor R$ 118.845,41; menor R$ 106.157,68
Status ANSWER · 3 ms · Tokens totais 20.959 · Entrada 20.026 · Cache 18.658 · Saída 933
**Latência total cronometrada pelo testador (Enter → resposta): 10,94 s**
```
SELECT nome AS servidor, cargo, lotacao, rendimento_liquido
FROM agora.remuneracoes
WHERE ano = 2025
  AND mes = 6
ORDER BY rendimento_liquido DESC NULLS LAST
LIMIT 10
```
Geração do SQL: 18.661 · 18.658 · 387 · 19.048 | Resposta final: 1.365 · 0 · 546 · 1.911

### Interface (EV-I01 a EV-I09) · 25/11, ~09h01 a ~09h45 [declarada pelo testador]
Título "Converse com os dados da organização"; campo "Digite sua pergunta" e botão "Perguntar"; texto "Pressione Enter para enviar", e o envio por Enter funcionou; durante a execução, o botão exibiu "Processando...", a área de resposta exibiu "Consultando os dados..." e o indicador mudou de "Sistema disponível" para "Verificando sistema..."; quatro atalhos ("Registros de remuneração em janeiro", "Servidores por unidade judiciária", "Ranking em tabela", "Evolução mensal"); o clique em atalho preencheu o campo sem enviar.

### Painel "Detalhes técnicos" · ~09h45
Testador: abre e fecha ao clicar no título; se estava aberto, permanece aberto na resposta seguinte.

### P1–P5 — prints · ~09h50
Ver `P1_jan2025_9484.png`, `P2_tabela_mensal.png`, `P3_processos_judiciais.png`, `P4_marco_2024.png`, `P5_ranking_sanitizado.png`.
- P1 [campo] "Quantos registros de remuneração existem em janeiro de 2025?" → "Em janeiro de 2025, existem 9.484 registros de remuneração." · ANSWER · 1781 ms (SQL fora do print)
- P2 [campo] pergunta de T02 → mesmos 6 valores; gráfico com rótulos do eixo Y exibidos como "1,4"
- P3 [campo] pergunta de T10 → NOT_ANSWERABLE · 18.680 tokens · cache 18.637 · saída 40
- P4 [campo] pergunta de T11 → "Em março de 2024, existem 0 registros de remuneração." · ANSWER · 0 ms · 19.641 tokens · cache 18.638 · mesmo SQL de T11
- P5 [campo] pergunta de T15 → mesmas 10 linhas (nomes pixelados na versão sanitizada)

### R1–R7 — atalho "Registros de remuneração em janeiro", 7 envios [atalho; declarado pelo testador] · ~10h09
Todas: resposta com 1.338 registros; SQL `SELECT COUNT(*) AS quantidade_registros FROM agora.remuneracoes WHERE ano = 2025 AND mes = 1` (com ou sem quebras de linha); resposta final 789 · 0 · 29 · 818.
| Exec. | Tempo | Tokens totais | Saída | Cache (geração) |
|---|---|---|---|---|
| R1 | 0 ms | 19.578 | 148 | 18.638 |
| R2 | 0 ms | 19.598 | 168 | 18.638 |
| R3 | 0 ms | 19.650 | 220 | 18.638 |
| R4 | 0 ms | 19.628 | 198 | 18.638 |
| R5 | 1 ms | 19.603 | 173 | 18.638 |
| R6 | 0 ms | 19.604 | 174 | 18.638 |
| R7 | 0 ms | 19.613 | 183 | 18.638 |
Intercalado entre R5 e R6: atalho "Servidores por unidade judiciária" → 545 · ANSWER · 12 ms · 19.696 tokens · cache 18.640.

### Repetições · ~10h15
- "Ranking em tabela" [campo] → mesmas 10 linhas · ANSWER · 2 ms · 20.833 tokens · cache 18.658 · SQL: `SELECT nome AS servidor, cargo, lotacao_canonica AS lotacao, rendimento_liquido FROM agora.vw_remuneracoes_semanticas WHERE ano = 2025 AND mes = 6 ORDER BY rendimento_liquido DESC NULLS LAST LIMIT 10`
- "Evolução mensal" [atalho] → mesmos valores de X4, em lista, com a frase "O rendimento atingiu o maior valor em março, caiu em abril e voltou a crescer em maio e junho." · sem tabela e sem visualização · ANSWER · 49 ms · 20.016 tokens · cache 0 · SQL igual ao de X4
- "Servidores por unidade judiciária" [atalho] → 545 · 1 ms · 19.688 tokens · cache 18.640
- "Registros de remuneração em janeiro" [atalho] → "Foram identificados 1.338 registros de remuneração em janeiro de 2025." · 0 ms · 19.659 tokens · cache 18.638

### T14 — `/health` · ~10h17
`{"status":"ok","database":"ok"}`

### T07 — "Quantas unidades existem?" [sugerida+eco] · ~10h17
Resposta: "Existem 344 unidades." · ANSWER · 20 ms · 19.582 tokens · cache 0
```
SELECT COUNT(DISTINCT unidade) AS quantidade_unidades
FROM agora.unidades_tlp
```

### T08 — "Quantas linhas existem na tabela de unidades da TLP, contando todas, inclusive repetidas?" [sugerida+eco] · ~10h17
Resposta: "Existem 369 linhas na tabela de unidades da TLP, contando todas, inclusive as repetidas." · ANSWER · 2 ms · 19.580 tokens · cache 0
```
SELECT COUNT(*) AS quantidade_linhas FROM agora.unidades_tlp
```

### T16 — "Quantos lançamentos de rubricas da folha existem em janeiro de 2025?" [sugerida+eco] · ~10h29
Resposta: "Em janeiro de 2025, existem 9.484 lançamentos de rubricas da folha." · ANSWER · 419 ms · 19.631 tokens · cache 0
```
SELECT COUNT(*) AS quantidade_lancamentos
FROM agora.fato_remuneracao_rubrica
WHERE referencia = DATE '2025-01-01'
```

### T09a — "Ranking da remuneração por unidade em janeiro" [sugerida; confirmada pelo testador] · ~10h36
"Preciso de mais detalhes. Qual ano de janeiro você deseja consultar e qual medida de remuneração deve ser usada no ranking: total de créditos, rendimento líquido ou outra?" · NEEDS_CLARIFICATION · 18.890 tokens · SQL —

### T09b — "Qual foi o maior valor?" [sugerida; confirmada pelo testador] · ~10h36
"Preciso de mais detalhes. Maior valor de qual informação, período ou categoria? Por exemplo: remuneração líquida, total de créditos, retenção de teto ou valor de uma rubrica." · NEEDS_CLARIFICATION · 18.724 tokens · SQL —

---

## 26/11/2026

### T17 — "quantas tabelas e quantas colunas existem?" [declarada] · ~09h40
"A LLM retornou QUERY sem uma instrução SQL." · FORMAT_ERROR · Tempo — · Tokens totais 19.736 · Entrada 18.638 · Cache 0 · Saída 1.098 · SQL —

### P6 — pergunta de T02 · 27/11/2026, ~09h10
Gráfico "Evolução — Quantidade de registros", 6 períodos; dica sobre o ponto de fevereiro: "Fevereiro — Quantidade de registros: 1,38"; eixo Y com rótulos "1,4". Ver `P6_grafico_tooltip_fevereiro.png`.
