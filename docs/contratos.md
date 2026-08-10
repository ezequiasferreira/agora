# Contratos de Integração do MVP Ágora

Este documento define como os módulos do MVP devem trocar informações entre si.

O objetivo é permitir que cada integrante desenvolva sua parte de forma independente, mas com entradas e saídas padronizadas.

---

## 1. Banco de Dados → Catálogo

**Responsável principal:** Gabriel

### Entrada

- PostgreSQL
- Database: `agora`
- Schema: `agora`

O módulo deve descobrir automaticamente:

- tabelas;
- colunas;
- tipos de dados;
- campos nulos ou obrigatórios;
- chaves primárias;
- chaves estrangeiras.

### Saída esperada

Arquivo:

`data_catalog.json`

Exemplo:

~~~json
{
  "database": "agora",
  "schema": "agora",
  "tables": [
    {
      "name": "remuneracoes",
      "columns": [
        {
          "name": "nome",
          "type": "text",
          "nullable": false
        }
      ],
      "primary_key": ["id"],
      "foreign_keys": []
    }
  ]
}
~~~

---

## 2. Catálogo → LLM

**Responsável principal:** Mateus

### Entrada

- pergunta do usuário em linguagem natural;
- arquivo `data_catalog.json`.

A LLM deve utilizar o catálogo para compreender quais dados estão disponíveis.

A solução não deve depender de nomes de tabelas ou colunas cadastrados manualmente no código.

### Saídas possíveis

#### QUERY

Quando a pergunta puder ser respondida:

~~~json
{
  "status": "QUERY",
  "sql": "SELECT ...",
  "message": null
}
~~~

#### NOT_ANSWERABLE

Quando os dados disponíveis não forem suficientes:

~~~json
{
  "status": "NOT_ANSWERABLE",
  "sql": null,
  "message": "Os dados disponíveis não permitem responder essa pergunta."
}
~~~

#### NEEDS_CLARIFICATION

Quando a pergunta estiver ambígua:

~~~json
{
  "status": "NEEDS_CLARIFICATION",
  "sql": null,
  "message": "É necessário esclarecer a pergunta antes da consulta."
}
~~~

---

## 3. LLM → API

**Responsáveis principais:** Mateus e Gelson

A LLM não deve executar SQL diretamente no PostgreSQL.

O SQL gerado deverá ser enviado para a API.

### Endpoint

`POST /query`

### Entrada

~~~json
{
  "sql": "SELECT ..."
}
~~~

---

## 4. API → PostgreSQL

**Responsável principal:** Gelson

Antes da execução, a API deve validar a consulta.

### Requisitos mínimos

- somente consultas de leitura;
- bloquear `INSERT`;
- bloquear `UPDATE`;
- bloquear `DELETE`;
- bloquear `DROP`;
- bloquear `ALTER`;
- bloquear `TRUNCATE`;
- impedir múltiplas instruções;
- limitar quantidade de registros;
- aplicar timeout;
- utilizar usuário PostgreSQL somente leitura.

---

## 5. API → LLM

### Resposta de sucesso

~~~json
{
  "success": true,
  "columns": [
    "nome",
    "rendimento_liquido"
  ],
  "rows": [
    [
      "Exemplo",
      10000.00
    ]
  ],
  "row_count": 1,
  "execution_time_ms": 25
}
~~~

### Resposta de erro

~~~json
{
  "success": false,
  "error_type": "SQL_VALIDATION_ERROR",
  "message": "Consulta não permitida."
}
~~~

---

## 6. Fluxo completo esperado

~~~text
Pergunta do usuário
        ↓
       LLM
        ↓
Consulta ao catálogo
        ↓
   Geração de SQL
        ↓
      API
        ↓
Validação de segurança
        ↓
   PostgreSQL
        ↓
Resultado estruturado
        ↓
       LLM
        ↓
Resposta ao usuário
~~~

---

## 7. Regra de independência

Cada módulo deve funcionar de forma independente.

O contrato define apenas:

- o que cada módulo recebe;
- o que cada módulo entrega.

A implementação interna fica sob responsabilidade de cada integrante.

---

## 8. Critério de integração

O MVP será considerado integrado quando uma pergunta em linguagem natural conseguir percorrer todo o fluxo:

**Pergunta → LLM → SQL → API → PostgreSQL → resultado → resposta final**
