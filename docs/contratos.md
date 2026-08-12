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

### Critério mínimo de aceite

O catálogo estrutural deve ser gerado automaticamente a partir do PostgreSQL.

Se uma nova tabela for adicionada ao schema `agora`, o extrator deve identificá-la automaticamente na próxima execução, sem cadastro manual.

---

### Enriquecimento semântico automático

Além da estrutura mínima obrigatória, o catálogo poderá identificar automaticamente valores de domínio de colunas adequadas para esse tipo de descoberta.

O objetivo é permitir que a LLM compreenda valores existentes no banco sem depender de:

- hardcode;
- conhecimento externo;
- valores cadastrados manualmente;
- suposições sobre códigos ou categorias.

Exemplo:

~~~json
{
  "name": "grau_jurisdicao",
  "type": "text",
  "nullable": true,
  "distinct_values": [
    "UNIDADE JUDICIÁRIA DE PRIMEIRO GRAU",
    "UNIDADE JUDICIÁRIA DE SEGUNDO GRAU"
  ]
}
~~~

### Regras para enriquecimento

O enriquecimento semântico deve:

- ser obtido automaticamente a partir do PostgreSQL;
- não exigir cadastro manual de valores;
- ser utilizado apenas quando a cardinalidade da coluna permitir esse tipo de descoberta;
- possuir limite configurável para quantidade de valores distintos;
- não incluir indiscriminadamente campos de alta cardinalidade;
- não incluir dados potencialmente sensíveis ou identificadores pessoais apenas para fins de enriquecimento;
- preservar o catálogo estrutural mesmo quando o enriquecimento não puder ser realizado.

Exemplos de campos que normalmente não devem ter seus valores incorporados ao catálogo:

- nomes de pessoas;
- matrículas;
- CPF;
- CNPJ;
- documentos;
- identificadores únicos;
- textos livres de alta cardinalidade.

### Objetivo do enriquecimento

Permitir que perguntas em linguagem natural utilizem categorias e valores realmente existentes no banco sem que a LLM precise inventar classificações ou valores de filtro.

Exemplo:

Pergunta:

> Quantos servidores pertencem às unidades judiciárias de primeiro e segundo graus?

Se o catálogo informar que a coluna `grau_jurisdicao` possui valores como:

- `UNIDADE JUDICIÁRIA DE PRIMEIRO GRAU`;
- `UNIDADE JUDICIÁRIA DE SEGUNDO GRAU`;

a LLM poderá utilizar esses valores reais na geração da consulta.

O enriquecimento semântico é complementar ao catálogo estrutural e não altera o critério mínimo de aceite originalmente definido para o módulo.

---

## 2. Catálogo → LLM

**Responsável principal:** Mateus

### Entrada

- pergunta do usuário em linguagem natural;
- arquivo `data_catalog.json`.

A LLM deve utilizar o catálogo para compreender quais dados estão disponíveis.

A solução não deve depender de nomes de tabelas, colunas, relacionamentos ou valores cadastrados manualmente no código.

### Regras

A LLM deve:

- utilizar somente tabelas existentes no catálogo;
- utilizar somente colunas existentes no catálogo;
- utilizar somente relacionamentos explicitamente disponíveis no catálogo;
- não inventar valores de domínio;
- não inventar códigos;
- não inventar relacionamentos;
- gerar apenas consultas de leitura;
- reconhecer quando os dados disponíveis não permitem responder à pergunta;
- reconhecer quando a pergunta necessita de esclarecimento.

### Saídas semânticas possíveis

#### QUERY

Quando a pergunta puder ser respondida com segurança:

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

### Estados técnicos

Falhas técnicas não devem ser confundidas com limitações dos dados.

#### PROVIDER_ERROR

Utilizado quando ocorrer falha de comunicação, autenticação, timeout, limite de requisições ou indisponibilidade do provedor de Inteligência Artificial.

Exemplo:

~~~json
{
  "status": "PROVIDER_ERROR",
  "sql": null,
  "message": "Não foi possível acessar o provedor de Inteligência Artificial."
}
~~~

`PROVIDER_ERROR` não significa que os dados são insuficientes.

#### FORMAT_ERROR

Utilizado quando o provedor retornar uma resposta incompatível com o contrato esperado.

Exemplo:

~~~json
{
  "status": "FORMAT_ERROR",
  "sql": null,
  "message": "A resposta do provedor não possui o formato esperado."
}
~~~

---

## 3. Provedores de Inteligência Artificial

O módulo LLM deve permanecer independente de fornecedor.

A implementação poderá utilizar diferentes provedores desde que respeitem o mesmo contrato de entrada e saída.

### Provedor principal do MVP

OpenAI

Modelo inicialmente utilizado:

`gpt-5.6-luna`

### Provedor alternativo

Google Gemini

A escolha do provedor deve ocorrer por configuração, sem necessidade de alteração da lógica principal da aplicação.

Exemplo:

~~~text
LLM_PROVIDER=openai
~~~

ou:

~~~text
LLM_PROVIDER=gemini
~~~

### Princípio

O Ágora não deve depender de um modelo específico de Inteligência Artificial.

A camada de LLM deve ser intercambiável.

---

## 4. LLM → API

**Responsáveis principais:** Mateus e Gelson

A LLM não deve executar SQL diretamente no PostgreSQL.

Quando o status for `QUERY`, o SQL gerado deverá ser enviado para a API do Ágora.

### Endpoint

`POST /query`

### Entrada

~~~json
{
  "sql": "SELECT ..."
}
~~~

Quando o status for:

- `NOT_ANSWERABLE`;
- `NEEDS_CLARIFICATION`;
- `PROVIDER_ERROR`;
- `FORMAT_ERROR`;

nenhuma consulta SQL deve ser enviada ao banco.

---

## 5. API → PostgreSQL

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
- bloquear `CREATE`;
- bloquear `GRANT`;
- bloquear `REVOKE`;
- impedir múltiplas instruções;
- limitar quantidade de registros;
- aplicar timeout;
- utilizar sessão PostgreSQL somente leitura.

### Princípio de segurança

A LLM nunca deve possuir acesso direto ao PostgreSQL.

A API é a camada responsável por validar e controlar toda consulta antes da execução.

Fluxo obrigatório:

~~~text
LLM
 ↓
SQL
 ↓
API
 ↓
Validação
 ↓
PostgreSQL
~~~

---

## 6. API → LLM

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
  "execution_time_ms": 25,
  "executed_sql": "SELECT ..."
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

## 7. Fluxo completo esperado

~~~text
Pergunta do usuário
        ↓
       LLM
        ↓
Consulta ao catálogo
        ↓
Análise da disponibilidade dos dados
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

## 8. Regra de independência

Cada módulo deve funcionar de forma independente.

O contrato define:

- o que cada módulo recebe;
- o que cada módulo entrega;
- os estados permitidos;
- os limites de responsabilidade entre os módulos.

A implementação interna fica sob responsabilidade de cada integrante.

A integração não deve exigir conhecimento interno da implementação dos demais módulos.

---

## 9. Regra de não utilização de hardcode

O MVP deve evitar cadastrar manualmente no código:

- nomes de tabelas;
- nomes de colunas;
- relacionamentos;
- valores de domínio;
- classificações específicas do banco conectado.

Essas informações devem ser descobertas automaticamente sempre que tecnicamente possível.

O objetivo é permitir que o Ágora seja conectado futuramente a outras bases sem necessidade de reprogramação específica para cada banco.

---

## 10. Critério de integração

O MVP será considerado integrado quando uma pergunta em linguagem natural conseguir percorrer todo o fluxo:

**Pergunta → catálogo → LLM → SQL → API → PostgreSQL → resultado → resposta final**

Também deverá demonstrar corretamente situações em que:

- os dados não permitem responder;
- a pergunta é ambígua;
- o provedor de IA apresenta erro técnico;
- a resposta do provedor apresenta formato inválido;
- uma consulta SQL perigosa é bloqueada pela API.

---

## 11. Princípio central do Ágora

O Ágora deve priorizar:

- precisão;
- rastreabilidade;
- segurança;
- independência de fornecedor;
- descoberta automática;
- reutilização em diferentes bases de dados.

Quando houver conflito entre gerar uma resposta aparentemente útil e preservar a integridade dos dados, o sistema deve priorizar a integridade e a rastreabilidade.
