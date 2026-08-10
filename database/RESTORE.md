# Restauração da Base PostgreSQL do Ágora

O arquivo `agora.dump` contém uma cópia da base utilizada no MVP.

Por conter dados reais do projeto, esse arquivo não é versionado no GitHub e deve ser compartilhado separadamente entre os integrantes da equipe.

---

## Ambiente esperado

- PostgreSQL
- Database: `agora`
- Schema: `agora`

---

## Restauração pelo DBeaver

1. Criar um database PostgreSQL chamado `agora`.
2. Clicar com o botão direito no database.
3. Selecionar `Tools → Restore`.
4. Selecionar o arquivo `agora.dump`.
5. Executar a restauração.

---

## Validação após a restauração

Confirmar a existência do schema:

`agora`

E das tabelas:

- `agora.remuneracoes`
- `agora.servidores_tlp`
- `agora.unidades_tlp`
- `agora.unidades_tlp_cargos_funcoes`
- `agora.rubricas_folha`

---

## Totais esperados

| Estrutura | Quantidade |
|---|---:|
| Remunerações | 8.124 registros |
| Servidores TLP | 1.136 |
| Unidades TLP | 369 |
| Rubricas | 194 |

---

## Importante

O arquivo `agora.dump` não deve ser enviado ao repositório.

O código e a estrutura reproduzível da base estão versionados em:

- `database/ddl/`
- `database/scripts/`
