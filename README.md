# Ágora

Plataforma inteligente para integração, descoberta e consulta de dados funcionais e remuneratórios do TJRR.

O MVP do Ágora está sendo desenvolvido para demonstrar que diferentes fontes de dados podem ser integradas, descobertas automaticamente e consultadas em linguagem natural com segurança e rastreabilidade.

---

## Objetivo do MVP

Permitir que o usuário faça uma pergunta em linguagem natural e receba uma resposta baseada nos dados disponíveis no PostgreSQL.

Fluxo esperado:

~~~text
Pergunta do usuário
        ↓
       LLM
        ↓
Catálogo automático
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

## Estrutura do projeto

~~~text
agora/
│
├── api/
│   └── API segura de consultas
│
├── catalog/
│   └── Descoberta automática do banco
│
├── database/
│   └── Scripts e estrutura PostgreSQL
│
├── docs/
│   └── Arquitetura, contratos e acompanhamento
│
├── integration/
│   └── Testes de integração ponta a ponta
│
├── llm/
│   └── Linguagem natural e geração de SQL
│
└── reports/
    └── Resultados, evidências e evolução do MVP
~~~

---

## Responsáveis

| Frente | Responsável |
|---|---|
| Coordenação e Dados | Ezequias |
| Catálogo automático | Gabriel |
| API de consultas | Gelson |
| Linguagem Natural / SQL | Mateus |
| Integração | Equipe |

---

## Base atual do MVP

O PostgreSQL do MVP utiliza:

- Database: `agora`
- Schema: `agora`

Dados atualmente carregados:

- 8.124 registros de remuneração;
- 1.136 vínculos funcionais da TLP;
- 369 unidades;
- 207 cargos em comissão;
- 317 funções de confiança;
- 194 rubricas da folha.

As fontes utilizadas são dados reais do Portal da Transparência do TJRR referentes ao domínio de Gestão de Pessoas.

---

## Módulos

### Catalog

Responsável por descobrir automaticamente a estrutura do PostgreSQL e gerar:

`data_catalog.json`

---

### LLM

Responsável por receber:

- pergunta em linguagem natural;
- catálogo automático.

E retornar:

- `QUERY`;
- `NOT_ANSWERABLE`;
- `NEEDS_CLARIFICATION`.

---

### API

Responsável por:

- receber SQL;
- validar a consulta;
- bloquear comandos perigosos;
- executar somente consultas permitidas;
- devolver resultados estruturados.

---

## Contratos

Os contratos de integração estão documentados em:

`docs/contratos.md`

---

## Status

O acompanhamento do MVP está disponível em:

`docs/status_mvp.md`

---

## Meta de integração

O primeiro grande marco do MVP é executar com sucesso:

**Pergunta → LLM → SQL → API → PostgreSQL → resultado → resposta**

---

## Princípio do projeto

Os módulos devem ser independentes.

Cada componente conhece apenas suas entradas e suas saídas.

A estrutura interna de cada módulo pode evoluir sem quebrar os demais, desde que os contratos de integração sejam respeitados.
