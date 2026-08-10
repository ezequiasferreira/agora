import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db  # noqa: E402
from app.main import app  # noqa: E402


def banco_disponivel() -> bool:
    try:
        return db.verificar_conexao()
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not banco_disponivel(),
    reason="Banco de dados não acessível nas configurações atuais (DB_*).",
)

client = TestClient(app)


def test_health():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_query_simples():
    resposta = client.post(
        "/query",
        json={"sql": "SELECT 1 AS um"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["success"] is True
    assert corpo["columns"] == ["um"]
    assert corpo["rows"] == [[1]]
    assert corpo["row_count"] == 1
    assert "execution_time_ms" in corpo
    assert corpo["executed_sql"] == "SELECT 1 AS um"


def test_query_remove_ponto_virgula_final():
    resposta = client.post(
        "/query",
        json={"sql": "SELECT 2 AS dois ;"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["executed_sql"] == "SELECT 2 AS dois"


def test_query_bloqueada_drop():
    resposta = client.post(
        "/query",
        json={"sql": "DROP TABLE agora.remuneracoes"},
    )
    assert resposta.status_code == 400
    corpo = resposta.json()
    assert corpo["success"] is False
    assert corpo["error_type"] == "SQL_VALIDATION_ERROR"


def test_query_multiplas_instrucoes():
    resposta = client.post(
        "/query",
        json={"sql": "SELECT 1; DELETE FROM agora.remuneracoes"},
    )
    assert resposta.status_code == 400
    corpo = resposta.json()
    assert corpo["success"] is False
    assert corpo["error_type"] == "MULTIPLE_STATEMENTS_ERROR"


def test_query_nao_select():
    resposta = client.post(
        "/query",
        json={"sql": "UPDATE agora.remuneracoes SET nome = 'x'"},
    )
    assert resposta.status_code == 400
    assert resposta.json()["error_type"] == "SQL_VALIDATION_ERROR"