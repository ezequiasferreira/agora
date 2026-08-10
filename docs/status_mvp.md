# Status do MVP Ágora

Este documento apresenta o acompanhamento gerencial do MVP, com o estado atual das frentes de trabalho, responsáveis e próximas entregas.

---

## Status geral

| Frente | Responsável | Status |
|---|---|---|
| Base de dados real do TJRR | Ezequias | ✅ Concluído |
| PostgreSQL do MVP | Ezequias | ✅ Concluído |
| Validação das cargas | Ezequias | ✅ Concluído |
| Catálogo automático do banco | Gabriel | 🟡 Em desenvolvimento |
| API segura de consultas | Gelson | 🟡 Em desenvolvimento |
| Linguagem natural → SQL | Mateus | 🟡 Em desenvolvimento |
| Integração entre módulos | Equipe | 🔴 Próxima etapa |
| Pergunta ponta a ponta | Equipe | 🔴 Meta seguinte |

---

## Resultados já alcançados

### Banco PostgreSQL

- Database: `agora`
- Schema: `agora`

### Dados carregados

| Fonte | Quantidade |
|---|---:|
| Remunerações do 1º semestre de 2025 | 8.124 registros |
| Servidores / vínculos da TLP | 1.136 |
| Unidades da TLP | 369 |
| Cargos em comissão | 207 |
| Funções de confiança | 317 |
| Rubricas da folha | 194 |

### Validações

- cargas concluídas com sucesso;
- créditos, débitos e rendimento líquido validados;
- 194 códigos de rubrica distintos;
- 99,65% dos nomes da TLP encontrados na base de remuneração.

---

## Entregas por responsável

### Ezequias — Coordenação e Dados

**Concluído:**

- preparação da base real do TJRR;
- carga das remunerações;
- carga da TLP;
- carga das rubricas;
- validações dos dados;
- definição dos contratos de integração;
- organização inicial do repositório GitHub.

**Próxima atuação:**

- coordenar a integração entre os módulos;
- manter os contratos atualizados;
- organizar os testes e evidências;
- acompanhar bloqueios e dependências.

---

### Gabriel — Catálogo Automático

**Objetivo:**

Conectar ao PostgreSQL e descobrir automaticamente a estrutura do schema `agora`.

**Entrada:**

- PostgreSQL;
- database `agora`;
- schema `agora`.

**Saída esperada:**

`data_catalog.json`

O catálogo deve conter, no mínimo:

- tabelas;
- colunas;
- tipos;
- nullable;
- chaves primárias;
- chaves estrangeiras.

**Critério de aceite:**

Se uma nova tabela for adicionada ao schema `agora`, o extrator deve identificá-la automaticamente na próxima execução.

---

### Gelson — API de Consultas

**Objetivo:**

Criar uma API segura para receber e executar consultas SQL de leitura.

**Entrada:**

~~~json
{
  "sql": "SELECT ..."
}
~~~

**Saída esperada:**

~~~json
{
  "success": true,
  "columns": [],
  "rows": [],
  "row_count": 0,
  "execution_time_ms": 0
}
~~~

**Requisitos mínimos:**

- permitir somente leitura;
- bloquear comandos perigosos;
- impedir múltiplas instruções;
- limitar quantidade de registros;
- aplicar timeout;
- usar usuário PostgreSQL somente leitura.

---

### Mateus — Linguagem Natural → SQL

**Objetivo:**

Receber a pergunta do usuário e utilizar o catálogo automático para gerar SQL.

**Entrada:**

- pergunta em linguagem natural;
- `data_catalog.json`.

**Saídas possíveis:**

- `QUERY`
- `NOT_ANSWERABLE`
- `NEEDS_CLARIFICATION`

**Critério de aceite:**

O módulo não deve depender de nomes de tabelas ou colunas cadastrados manualmente no código.

---

## Interações entre as partes

~~~text
Banco PostgreSQL
      ↓
Gabriel
      ↓
data_catalog.json
      ↓
Mateus
      ↓
SQL
      ↓
Gelson
      ↓
PostgreSQL
      ↓
JSON com resultado
      ↓
Mateus
      ↓
Resposta ao usuário
~~~

---

## Meta imediata

A próxima meta da equipe é fazer os módulos começarem a conversar entre si.

O primeiro marco de integração será:

**Pergunta → LLM → SQL → API → PostgreSQL → resultado → resposta**

Não é necessário começar com uma pergunta complexa.

Uma primeira pergunta de teste pode ser:

> Quantos registros de remuneração existem em janeiro de 2025?

---

## Indicador principal

### O Ágora consegue responder uma pergunta de ponta a ponta?

**Status atual:** 🟡 Em preparação para integração.

**Próxima meta:** 🟢 Sim.
