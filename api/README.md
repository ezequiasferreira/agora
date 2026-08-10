# API de Consultas do Ágora

API segura de leitura: recebe SQL, valida a instrução, executa no PostgreSQL e devolve o resultado em formato estruturado.

Ela é a camada de consulta do MVP Ágora — o SQL pode vir do módulo de Linguagem Natural (LLM), mas a API nunca executa diretamente qualquer instrução sem antes validar a segurança.

Responsável principal: Gelson.

---

## Visão geral

Fluxo de uma consulta:

```
SQL recebido pelo client
      ↓
Validação de segurança (api/app/query_validator.py)
      ↓
Execução somente leitura (api/app/db.py)
      ↓
Resposta estruturada (api/app/main.py)
```

- Só aceita `SELECT`;
- Bloqueia comandos perigosos;
- Impede múltiplas instruções;
- Aplica timeout e limite de linhas;
- Utiliza sessão somente leitura no banco.

---

## Pré-requisitos

- Python 3.11 ou superior (testado na 3.14);
- Um PostgreSQL acessível (host, porta, usuário e senha configuráveis via variáveis no `.env`);
- Porta `8000` livre (ou ajuste o `--port` do uvicorn).

> A configuração do servidor de banco (instalação, Docker, etc.) não faz parte deste guia.

---

## Configuração

A API lê as configurações de um arquivo `.env` na pasta `api/`. Como esse arquivo é privado (ignorado pelo git), crie-o manualmente com o conteúdo abaixo e ajuste os valores:

```bash
# api/.env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agora
DB_USER=postgres
DB_PASSWORD=sua_senha
QUERY_TIMEOUT_MS=3000
MAX_ROWS=1000
```

### Variáveis disponíveis

| Variável | Padrão | Descrição |
|---|---|---|
| `DB_HOST` | `localhost` | Endereço do servidor PostgreSQL |
| `DB_PORT` | `5432` | Porta do PostgreSQL |
| `DB_NAME` | `agora` | Nome do banco de dados |
| `DB_USER` | `postgres` | Usuário da conexão |
| `DB_PASSWORD` | — | Senha do usuário |
| `QUERY_TIMEOUT_MS` | `3000` | Tempo máximo de execução de uma consulta (ms) |
| `MAX_ROWS` | `1000` | Limite de linhas retornadas por consulta |

O banco não precisa estar na máquina local: basta responder nos endereços acima, em qualquer ambiente.

---

## Instalação e execução

### Linux / macOS

```bash
cd api

# 1. Ambiente virtual
python3 -m venv .venv

# 2. Dependências
.venv/bin/pip install -r requirements.txt

# 3. Subir a API (recarga automática em desenvolvimento)
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Windows

```powershell
cd api

# 1. Ambiente virtual
py -m venv .venv

# 2. Dependências
.\.venv\Scripts\pip install -r requirements.txt

# 3. Subir a API (recarga automática em desenvolvimento)
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Ao subir:

- Swagger (interface interativa): http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Rodar a API em container

Para rodar a API em um container Docker (requer Docker e Compose na máquina):

```bash
# A partir da raiz do repositório, com o banco já acessível na rede do compose
docker compose -f api/docker-compose.api.yaml up -d --build
```

- A API sobe em http://localhost:8000 (Swagger em `/docs`);
- A configuração vem das mesmas variáveis do `api/.env`;
- Por padrão o container enxerga o banco pelo hostname `agora-db` na rede `api_default` — mantenha o compose do banco de pé antes;
- Se o banco estiver em outro endereço, informe-o para o container:

```bash
AGORA_DB_HOST=192.168.0.10 docker compose -f api/docker-compose.api.yaml up -d
```

Comandos úteis:

```bash
docker compose -f api/docker-compose.api.yaml up -d --build agora-api   # rebuild após mudanças no código
docker compose -f api/docker-compose.api.yaml logs -f agora-api          # acompanhar logs
docker compose -f api/docker-compose.api.yaml down                       # parar a API
```

---

## Como testar a API

### 1. Interface Swagger

Abra http://localhost:8000/docs e use a UI para chamar `GET /health` e `POST /query`.

### 2. Curl

```bash
# Saúde da API e do banco
curl http://localhost:8000/health
```

```bash
# Consulta válida
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT COUNT(*) AS total FROM agora.remuneracoes"}'
```

```bash
# Consulta bloqueada (espera-se HTTP 400)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"sql":"DROP TABLE agora.remuneracoes"}'
```

```bash
# Múltiplas instruções (espera-se HTTP 400)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT 1; DELETE FROM agora.remuneracoes"}'
```

No Windows PowerShell, o `curl` nativo é um alias do PowerShell; use `curl.exe`:

```powershell
curl.exe -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{\"sql\":\"SELECT 1 AS um\"}'
```

### 3. Testes automatizados

```bash
cd api
.venv/bin/python -m pytest tests/ -v        # Linux / macOS
.\.venv\Scripts\python -m pytest tests/ -v  # Windows
```

Os testes são agnósticos de ambiente: usam as variáveis `DB_*` do `.env`. Se o banco não estiver acessível no momento, os testes são **pulados (skip)**, não falham.

---

## Contrato do endpoint

### `POST /query`

**Entrada:**

```json
{
  "sql": "SELECT cargo, AVG(rendimento_liquido) AS media_rendimento FROM agora.remuneracoes GROUP BY cargo"
}
```

**Resposta de sucesso:**

```json
{
  "success": true,
  "columns": ["cargo", "media_rendimento"],
  "rows": [],
  "row_count": 0,
  "execution_time_ms": 24,
  "executed_sql": "SELECT cargo, AVG(rendimento_liquido) AS media_rendimento FROM agora.remuneracoes GROUP BY cargo"
}
```

Campos:

- `columns` / `rows` — colunas e linhas retornadas pelo banco (limitadas a `MAX_ROWS`);
- `row_count` — quantidade de linhas retornadas;
- `execution_time_ms` — tempo de execução no PostgreSQL;
- `executed_sql` — SQL normalizado que foi efetivamente executado (comentários e `;` final removidos), para rastreabilidade.

**Resposta de erro:**

```json
{
  "success": false,
  "error_type": "SQL_VALIDATION_ERROR",
  "message": "Consulta não permitida. Comando(s) bloqueado(s): DROP."
}
```

`error_type` possíveis:

- `SQL_VALIDATION_ERROR` — não é um `SELECT` ou contém comando bloqueado (HTTP 400);
- `MULTIPLE_STATEMENTS_ERROR` — mais de uma instrução no mesmo envio (HTTP 400);
- `QUERY_TIMEOUT` — excedeu `QUERY_TIMEOUT_MS` (HTTP 504);
- `DB_QUERY_ERROR` — erro do PostgreSQL ao executar (HTTP 500);
- `INTERNAL_ERROR` — erro não categorizado (HTTP 500).

### `GET /health`

```json
{
  "status": "ok",
  "database": "ok"
}
```

Retorna HTTP 503 e `"database": "error"` quando o banco não responde.

---

## Segurança aplicada

1. **Validador** (`query_validator.py`): remove comentários, exige `SELECT` como primeiro comando e bloqueia por token `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `INTO`, entre outros.
2. **Múltiplas instruções**: qualquer `;` além do final do comando é rejeitado.
3. **Sessão somente leitura**: a conexão abre transações `readonly` — qualquer tentativa de escrita falha no próprio PostgreSQL, mesmo que passe pelo validador.
4. **Timeout e limite**: `statement_timeout` configura a partir de `QUERY_TIMEOUT_MS`; as linhas são limitadas via `fetchmany(MAX_ROWS)`.

---

## Solução de problemas

**`Error loading ASGI app. Import string "main" must be in format "<module>:<attribute>".`**
Use o formato completo no uvicorn: `app.main:app` (ou `main:app` se estiver dentro da pasta `app/`).

**Testes pulados (skipped)**
O banco informado no `.env` não está acessível. Confira `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_PASSWORD`.

**Porta 8000 já em uso**
Mude a porta no comando do uvicorn: `--port 8001`.

**Erro de autenticação no PostgreSQL**
Confira `DB_NAME`, `DB_USER` e `DB_PASSWORD` no `api/.env`. O `.env` precisa estar na pasta `api/` (o programa o lê a partir do diretório de trabalho).