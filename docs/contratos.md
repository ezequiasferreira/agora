# Contratos de Integração do MVP Ágora

Este documento define como os módulos do MVP devem trocar informações entre si.

O objetivo é permitir que cada integrante desenvolva sua parte de forma independente, mas com entradas e saídas padronizadas.

---

## 1. Banco de Dados → Catálogo

Responsável principal: Gabriel

Entrada:

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

Saída esperada:

`data_catalog.json`

Exemplo:

```json
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
