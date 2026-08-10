# Banco de Dados do Projeto Ágora

Esta pasta contém a estrutura e os scripts utilizados para preparar o banco PostgreSQL do MVP do Ágora.

## Ambiente do MVP

- SGBD: PostgreSQL
- Database: `agora`
- Schema: `agora`

---

## Estrutura do banco

O arquivo:

`database/ddl/estrutura_agora.sql`

cria toda a estrutura necessária do schema `agora`.

Atualmente são criadas as seguintes tabelas:

- `agora.remuneracoes`
- `agora.servidores_tlp`
- `agora.unidades_tlp`
- `agora.unidades_tlp_cargos_funcoes`
- `agora.rubricas_folha`

---

## Como criar a estrutura localmente

1. Criar um database PostgreSQL chamado:

`agora`

2. Conectar ao database.

3. Executar:

`database/ddl/estrutura_agora.sql`

Após a execução, o schema `agora` e suas tabelas estarão disponíveis.

---

## Scripts de carga

Os scripts utilizados no MVP estão em:

`database/scripts/`

Principais arquivos:

- `carregar_remuneracoes_tjrr.py`
- `diagnosticar_integracao_tlp.py`
- `carregar_tlp_rubricas_tjrr.py`

---

## Dados

Os arquivos originais do TJRR não são versionados no Git.

Os dados utilizados no MVP foram obtidos de fontes públicas do Portal da Transparência do TJRR.

A base completa utilizada na integração será disponibilizada à equipe separadamente quando necessário.

---

## Uso pelo módulo de catálogo

O módulo `catalog/` deve conectar ao PostgreSQL e descobrir automaticamente a estrutura do schema:

`agora`

O extrator não deve depender da lista de tabelas apresentada neste documento.

Essa lista é apenas documentação.

A descoberta das tabelas, colunas, tipos, chaves primárias e chaves estrangeiras deve ocorrer diretamente no PostgreSQL.
