# Módulo LLM do Ágora

Este módulo é responsável por transformar perguntas em linguagem natural em consultas SQL compatíveis com o PostgreSQL utilizado pelo MVP.

---

## Entradas

O módulo recebe:

1. uma pergunta em linguagem natural;
2. um catálogo de dados em JSON.

Durante o desenvolvimento inicial, utilizar:

`llm/data_catalog.example.json`

Quando o módulo de catálogo estiver concluído, esse arquivo será substituído pelo `data_catalog.json` gerado automaticamente.

---

## Prompt-base

Utilizar as regras definidas em:

`llm/prompts/system_prompt.md`

O módulo deve seguir os contratos registrados em:

`docs/contratos.md`

---

## Saídas possíveis

O resultado deve ser um JSON válido contendo um dos seguintes estados:

- `QUERY`
- `NOT_ANSWERABLE`
- `NEEDS_CLARIFICATION`

---

## Regras principais

- utilizar somente tabelas e colunas presentes no catálogo;
- não criar nomes de tabelas manualmente no código;
- não criar nomes de colunas manualmente no código;
- não inventar relacionamentos;
- não utilizar conhecimento externo para responder perguntas sobre os dados;
- não executar SQL diretamente no PostgreSQL;
- gerar apenas consultas de leitura.

---

## Testes iniciais

### Teste 1 — consulta simples

Pergunta:

> Quantos registros de remuneração existem em janeiro de 2025?

Resultado esperado:

`QUERY`

Resultado esperado no PostgreSQL:

`1338`

---

### Teste 2 — agregação

Pergunta:

> Qual foi o total de rendimento líquido em junho de 2025?

Resultado esperado:

`QUERY`

---

### Teste 3 — informação inexistente

Pergunta:

> Qual é a formação acadêmica dos servidores?

Resultado esperado:

`NOT_ANSWERABLE`

---

### Teste 4 — pergunta ambígua

Pergunta:

> Qual foi a maior remuneração?

Resultado esperado:

`NEEDS_CLARIFICATION`

---

## Critério de aceite inicial

O módulo estará pronto para a primeira integração quando:

- [ ] conseguir carregar o catálogo;
- [ ] receber uma pergunta;
- [ ] enviar pergunta + catálogo para a LLM;
- [ ] retornar JSON válido;
- [ ] gerar SQL somente quando o status for `QUERY`;
- [ ] retornar `NOT_ANSWERABLE` quando faltarem dados;
- [ ] retornar `NEEDS_CLARIFICATION` quando houver ambiguidade;
- [ ] não possuir hardcode das tabelas atuais do MVP.

---

## Integração seguinte

Quando o status for:

`QUERY`

o campo:

`sql`

deverá ser enviado para:

`POST /query`

da API do Ágora.

Fluxo:

Pergunta  
→ catálogo  
→ LLM  
→ SQL  
→ API  
→ PostgreSQL  
→ resultado  
→ resposta final
