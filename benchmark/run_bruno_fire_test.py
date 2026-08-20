import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests


# ============================================================
# CAMINHOS
# ============================================================

DIRETORIO_ATUAL = Path(__file__).resolve().parent
DIRETORIO_RAIZ = DIRETORIO_ATUAL.parent

ARQUIVO_BENCHMARK = (
    DIRETORIO_ATUAL
    / "bruno_fire_test.json"
)

DIRETORIO_RESULTADOS = (
    DIRETORIO_ATUAL
    / "results"
)

API_URL = os.getenv(
    "AGORA_API_URL",
    "http://localhost:8000/ask",
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def carregar_benchmark() -> dict:
    with open(
        ARQUIVO_BENCHMARK,
        "r",
        encoding="utf-8",
    ) as arquivo:
        return json.load(arquivo)


def executar_pergunta(
    pergunta: str,
) -> dict:
    try:
        resposta = requests.post(
            API_URL,
            json={
                "question": pergunta
            },
            timeout=120,
        )

    except requests.RequestException as exc:
        return {
            "success": False,
            "status": "CONNECTION_ERROR",
            "answer": str(exc),
            "generated_sql": None,
            "columns": None,
            "rows": None,
            "row_count": None,
            "execution_time_ms": None,
            "usage": None,
        }

    try:
        corpo = resposta.json()

    except ValueError:
        return {
            "success": False,
            "status": "INVALID_RESPONSE",
            "answer": (
                "A API não retornou JSON válido."
            ),
            "generated_sql": None,
            "columns": None,
            "rows": None,
            "row_count": None,
            "execution_time_ms": None,
            "usage": None,
        }

    return corpo


def status_compativel(
    esperado: str,
    real: str,
) -> bool:
    """
    O benchmark inicial registra PARTIAL como estado
    esperado conceitualmente.

    Entretanto, o endpoint atual do Ágora ainda não
    possui um status PARTIAL nativo.

    Por isso, PARTIAL é considerado compatível quando
    o Ágora reconhece que não consegue responder
    integralmente e retorna:
    - NOT_ANSWERABLE
    - NEEDS_CLARIFICATION

    ANSWER para um caso PARTIAL também é registrado,
    mas deve ser revisado manualmente para verificar
    se houve extrapolação indevida dos dados.
    """

    if esperado == real:
        return True

    if esperado == "PARTIAL":
        return real in {
            "NOT_ANSWERABLE",
            "NEEDS_CLARIFICATION",
        }

    return False


def obter_tokens(
    resultado: dict,
) -> int | None:
    usage = resultado.get(
        "usage"
    )

    if not usage:
        return None

    return usage.get(
        "total_tokens"
    )


def obter_custo(
    resultado: dict,
) -> float | None:
    usage = resultado.get(
        "usage"
    )

    if not usage:
        return None

    cost = usage.get(
        "cost"
    )

    if not cost:
        return None

    return cost.get(
        "total_cost_usd"
    )


# ============================================================
# EXECUÇÃO DO BENCHMARK
# ============================================================

def main():
    benchmark = carregar_benchmark()

    casos = benchmark.get(
        "cases",
        [],
    )

    if not casos:
        print(
            "Nenhum caso encontrado no benchmark."
        )
        sys.exit(1)

    print()
    print("=" * 72)
    print("ÁGORA — TESTE DE FOGO DO PROF. BRUNO")
    print("=" * 72)
    print()

    resultados = []

    for indice, caso in enumerate(
        casos,
        start=1,
    ):
        caso_id = caso.get(
            "id"
        )

        titulo = caso.get(
            "title"
        )

        pergunta = caso.get(
            "question"
        )

        esperado = caso.get(
            "expected_status"
        )

        print(
            f"[{indice}/{len(casos)}] "
            f"{caso_id} — {titulo}"
        )

        print(
            f"Esperado: {esperado}"
        )

        resultado = executar_pergunta(
            pergunta
        )

        status_real = resultado.get(
            "status",
            "UNKNOWN",
        )

        compativel = status_compativel(
            esperado,
            status_real,
        )

        tokens = obter_tokens(
            resultado
        )

        custo = obter_custo(
            resultado
        )

        print(
            f"Real:     {status_real}"
        )

        if tokens is not None:
            print(
                f"Tokens:   {tokens}"
            )

        if custo is not None:
            print(
                f"Custo:    US$ {custo:.8f}"
            )

        print(
            "Resultado:",
            (
                "COMPATÍVEL"
                if compativel
                else "REVISAR"
            ),
        )

        print("-" * 72)

        resultados.append(
            {
                "case_id": caso_id,
                "title": titulo,
                "question": pergunta,
                "expected_status": esperado,
                "actual_status": status_real,
                "compatible": compativel,
                "answer": resultado.get(
                    "answer"
                ),
                "generated_sql": resultado.get(
                    "generated_sql"
                ),
                "columns": resultado.get(
                    "columns"
                ),
                "rows": resultado.get(
                    "rows"
                ),
                "row_count": resultado.get(
                    "row_count"
                ),
                "execution_time_ms": (
                    resultado.get(
                        "execution_time_ms"
                    )
                ),
                "usage": resultado.get(
                    "usage"
                ),
                "known_missing_data": caso.get(
                    "missing_data",
                    [],
                ),
                "semantic_risks": caso.get(
                    "semantic_risks",
                    [],
                ),
                "required_for_full_answer": (
                    caso.get(
                        "required_for_full_answer",
                        [],
                    )
                ),
                "notes": caso.get(
                    "notes"
                ),
            }
        )

    # ========================================================
    # RESUMO
    # ========================================================

    total = len(
        resultados
    )

    compativeis = sum(
        1
        for resultado in resultados
        if resultado["compatible"]
    )

    revisar = (
        total - compativeis
    )

    total_tokens = sum(
        (
            resultado["usage"]
            or {}
        ).get(
            "total_tokens",
            0,
        )
        for resultado in resultados
    )

    custo_total = sum(
        (
            (
                resultado["usage"]
                or {}
            ).get(
                "cost",
                {},
            )
            or {}
        ).get(
            "total_cost_usd",
            0,
        )
        for resultado in resultados
    )

    relatorio = {
        "benchmark": benchmark.get(
            "benchmark"
        ),
        "executed_at": datetime.now().isoformat(),
        "api_url": API_URL,
        "summary": {
            "total_cases": total,
            "compatible_cases": compativeis,
            "review_cases": revisar,
            "total_tokens": total_tokens,
            "estimated_total_cost_usd": round(
                custo_total,
                8,
            ),
        },
        "results": resultados,
    }

    DIRETORIO_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    arquivo_saida = (
        DIRETORIO_RESULTADOS
        / f"bruno_fire_test_{timestamp}.json"
    )

    with open(
        arquivo_saida,
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            relatorio,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 72)
    print("RESUMO")
    print("=" * 72)

    print(
        f"Casos:       {total}"
    )

    print(
        f"Compatíveis: {compativeis}"
    )

    print(
        f"Revisar:     {revisar}"
    )

    print(
        f"Tokens:      {total_tokens}"
    )

    print(
        f"Custo total: US$ {custo_total:.8f}"
    )

    print()
    print(
        "Relatório salvo em:"
    )

    print(
        arquivo_saida
    )


if __name__ == "__main__":
    main()
