import requests


API_URL_PADRAO = "http://localhost:8000/query"
TIMEOUT_SEGUNDOS = 10


def executar_sql_na_api(
    sql_gerado: str,
    url_api: str = API_URL_PADRAO,
) -> dict:
    """
    Envia uma consulta SQL para a API segura do Ágora.

    A função sempre retorna um dicionário estruturado.

    Em caso de sucesso, retorna a resposta original da API.

    Em caso de falha de rede, timeout ou resposta HTTP inválida,
    retorna um objeto com:

    {
        "success": false,
        "error_type": "...",
        "message": "..."
    }
    """

    payload = {
        "sql": sql_gerado
    }

    print(
        f"[Rede] Preparando envio para {url_api}..."
    )

    try:
        response = requests.post(
            url_api,
            json=payload,
            timeout=TIMEOUT_SEGUNDOS,
        )

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "API_TIMEOUT",
            "message": (
                "A API do Ágora excedeu o tempo limite "
                "de resposta."
            ),
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error_type": "API_CONNECTION_ERROR",
            "message": (
                "Não foi possível conectar à API do Ágora. "
                "Verifique se o serviço está em execução."
            ),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error_type": "API_REQUEST_ERROR",
            "message": (
                "Ocorreu uma falha de comunicação com "
                f"a API do Ágora: {exc}"
            ),
        }

    try:
        resposta_json = response.json()

    except ValueError:
        return {
            "success": False,
            "error_type": "API_INVALID_RESPONSE",
            "message": (
                "A API do Ágora retornou uma resposta "
                "que não está em formato JSON válido."
            ),
        }

    if response.status_code != 200:
        return {
            "success": False,
            "error_type": resposta_json.get(
                "error_type",
                "API_HTTP_ERROR",
            ),
            "message": resposta_json.get(
                "message",
                (
                    "A API do Ágora retornou "
                    f"HTTP {response.status_code}."
                ),
            ),
            "http_status": response.status_code,
        }

    return resposta_json
