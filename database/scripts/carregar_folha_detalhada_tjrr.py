import os
import random
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlencode

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import execute_values


load_dotenv()


DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "agora"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}


PORTAL_URL = (
    "https://remuneracoes.tjrr.jus.br/"
    "rhsysportaltransp/"
)

API_CONFIG_URL = (
    PORTAL_URL
    + "api/tracking/check-config"
)

API_REFERENCIAS_URL = (
    PORTAL_URL
    + "api/lov/referencia"
)

API_RELACAO_SERVIDORES_URL = (
    PORTAL_URL
    + "api/relacaoservidores"
)

API_FOLHA_URL = (
    PORTAL_URL
    + "api/relacaoservidores/folha"
)


USER_AGENT = (
    "Mozilla/5.0 "
    "(Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/151.0.0.0 "
    "Safari/537.36"
)


REFERENCIAS_CARGA = [
    "2025-01-01",
    "2025-02-01",
    "2025-03-01",
    "2025-04-01",
    "2025-05-01",
    "2025-06-01",
]


# Paralelismo deliberadamente moderado.
# O portal apresentou HTTP 503 com 6 workers.
MAX_WORKERS = 3

MAX_TENTATIVAS = 5

TAMANHO_LOTE_FOLHAS = 40

PAUSA_RETRY_BASE = 2.0


_thread_local = threading.local()


def converter_booleano(valor):
    if valor is None:
        return None

    if isinstance(valor, bool):
        return valor

    texto = str(valor).strip().lower()

    if texto in {
        "1",
        "true",
        "t",
        "sim",
        "s",
    }:
        return True

    if texto in {
        "0",
        "false",
        "f",
        "nao",
        "não",
        "n",
    }:
        return False

    return None


def converter_data(valor):
    if not valor:
        return None

    texto = str(valor).strip()

    formatos = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                texto,
                formato,
            ).date()

        except ValueError:
            continue

    return None


def montar_referencia_api(referencia):
    return (
        f"{referencia}"
        "T04:00:00Z[UTC]"
    )


def criar_sessao_http():
    sessao = requests.Session()

    sessao.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": (
                "application/json, "
                "text/plain, */*"
            ),
            "Accept-Language": (
                "pt-BR,pt;q=0.9,"
                "en-US;q=0.8,"
                "en;q=0.7"
            ),
            "Referer": PORTAL_URL,
        }
    )

    resposta = sessao.get(
        API_CONFIG_URL,
        timeout=60,
    )

    resposta.raise_for_status()

    resposta = sessao.get(
        API_REFERENCIAS_URL,
        timeout=60,
    )

    resposta.raise_for_status()

    return sessao


def obter_sessao_worker():
    sessao = getattr(
        _thread_local,
        "sessao",
        None,
    )

    if sessao is None:
        sessao = criar_sessao_http()

        _thread_local.sessao = sessao

    return sessao


def recriar_sessao_worker():
    sessao = getattr(
        _thread_local,
        "sessao",
        None,
    )

    if sessao is not None:
        try:
            sessao.close()
        except Exception:
            pass

    sessao = criar_sessao_http()

    _thread_local.sessao = sessao

    return sessao


def calcular_espera(
    tentativa,
    resposta=None,
):
    if resposta is not None:
        retry_after = resposta.headers.get(
            "Retry-After"
        )

        if retry_after:
            try:
                return max(
                    float(retry_after),
                    1.0,
                )
            except ValueError:
                pass

    espera = (
        PAUSA_RETRY_BASE
        * (2 ** (tentativa - 1))
    )

    # Pequeno jitter evita que os workers
    # repitam as chamadas exatamente juntos.
    espera += random.uniform(
        0.2,
        0.8,
    )

    return espera


def inicializar_sessao_principal():
    print(
        "Inicializando sessão principal..."
    )

    sessao = criar_sessao_http()

    print(
        "Sessão principal validada."
    )

    return sessao


def requisicao_json(
    sessao,
    url,
    parametros=None,
):
    ultimo_erro = None

    for tentativa in range(
        1,
        MAX_TENTATIVAS + 1,
    ):
        try:
            resposta = sessao.get(
                url,
                params=parametros,
                timeout=60,
            )

            if resposta.status_code == 200:
                return resposta.json()

            ultimo_erro = RuntimeError(
                "HTTP "
                f"{resposta.status_code}: "
                f"{resposta.text[:500]}"
            )

            if resposta.status_code in {
                429,
                500,
                502,
                503,
                504,
            }:
                if tentativa < MAX_TENTATIVAS:
                    espera = calcular_espera(
                        tentativa,
                        resposta,
                    )

                    time.sleep(
                        espera
                    )

                    continue

            resposta.raise_for_status()

        except (
            requests.RequestException,
            ValueError,
        ) as erro:
            ultimo_erro = erro

            if tentativa < MAX_TENTATIVAS:
                espera = calcular_espera(
                    tentativa
                )

                time.sleep(
                    espera
                )

                continue

    raise ultimo_erro


def listar_servidores_referencia(
    sessao,
    referencia,
):
    referencia_api = montar_referencia_api(
        referencia
    )

    pagina = 1
    servidores = []
    matriculas_vistas = set()
    total_informado = None

    while True:
        payload = requisicao_json(
            sessao=sessao,
            url=API_RELACAO_SERVIDORES_URL,
            parametros={
                "page": pagina,
                "referencia": referencia_api,
            },
        )

        if total_informado is None:
            total_informado = payload.get(
                "count"
            )

        dados = (
            payload.get(
                "dados"
            )
            or []
        )

        if not dados:
            break

        novos = 0

        for servidor in dados:
            matricula = servidor.get(
                "matricula"
            )

            if matricula is None:
                continue

            matricula = str(
                matricula
            )

            if matricula in matriculas_vistas:
                continue

            matriculas_vistas.add(
                matricula
            )

            servidores.append(
                servidor
            )

            novos += 1

        print(
            f"    página {pagina}: "
            f"{len(dados)} registros "
            f"({len(servidores)} acumulados)"
        )

        if (
            total_informado is not None
            and len(servidores)
            >= int(total_informado)
        ):
            break

        if novos == 0:
            break

        pagina += 1

    return servidores


def buscar_folhas_ja_carregadas(
    conn,
    referencia,
):
    referencia_date = datetime.strptime(
        referencia,
        "%Y-%m-%d",
    ).date()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT matricula
            FROM agora.fato_remuneracao_rubrica
            WHERE referencia = %s
            """,
            (
                referencia_date,
            ),
        )

        return {
            str(linha[0])
            for linha in cursor.fetchall()
        }


def consultar_folha_worker(
    matricula,
    referencia,
):
    referencia_api = montar_referencia_api(
        referencia
    )

    parametros = {
        "matricula": matricula,
        "referencia": referencia_api,
    }

    ultimo_erro = None

    for tentativa in range(
        1,
        MAX_TENTATIVAS + 1,
    ):
        sessao = obter_sessao_worker()

        try:
            resposta = sessao.get(
                API_FOLHA_URL,
                params=parametros,
                timeout=60,
            )

            if resposta.status_code == 200:
                endpoint_origem = (
                    f"{API_FOLHA_URL}?"
                    f"{urlencode(parametros)}"
                )

                return (
                    resposta.json(),
                    endpoint_origem,
                )

            if resposta.status_code == 440:
                ultimo_erro = RuntimeError(
                    "Sessão inválida HTTP 440"
                )

                recriar_sessao_worker()

                if tentativa < MAX_TENTATIVAS:
                    espera = calcular_espera(
                        tentativa,
                        resposta,
                    )

                    time.sleep(
                        espera
                    )

                    continue

            if resposta.status_code in {
                429,
                500,
                502,
                503,
                504,
            }:
                ultimo_erro = RuntimeError(
                    "HTTP "
                    f"{resposta.status_code}: "
                    f"{resposta.text[:300]}"
                )

                if tentativa < MAX_TENTATIVAS:
                    espera = calcular_espera(
                        tentativa,
                        resposta,
                    )

                    time.sleep(
                        espera
                    )

                    continue

            resposta.raise_for_status()

        except requests.RequestException as erro:
            ultimo_erro = erro

            if tentativa < MAX_TENTATIVAS:
                espera = calcular_espera(
                    tentativa
                )

                time.sleep(
                    espera
                )

                continue

    raise ultimo_erro


def transformar_folha_em_registros(
    matricula,
    referencia,
    payload,
    endpoint_origem,
):
    dados = (
        payload.get(
            "dados"
        )
        or {}
    )

    detalhes = (
        dados.get(
            "detalhesValorColuna"
        )
        or []
    )

    valores = (
        dados.get(
            "valoresColunas"
        )
        or {}
    )

    if not detalhes:
        return []

    matricula_api = valores.get(
        "matricula"
    )

    if (
        matricula_api is not None
        and str(matricula_api)
        != str(matricula)
    ):
        raise ValueError(
            "Matrícula retornada pela API "
            "difere da solicitada. "
            f"Solicitada={matricula}; "
            f"Retornada={matricula_api}"
        )

    nome_servidor = valores.get(
        "nmfuncionario"
    )

    codigo_cargo = valores.get(
        "cargo"
    )

    cargo = valores.get(
        "nmcargo"
    )

    codigo_setor = valores.get(
        "setor"
    )

    setor = valores.get(
        "nmsetor"
    )

    codigo_orgao = valores.get(
        "orgao"
    )

    orgao = valores.get(
        "nmorgao"
    )

    codigo_vinculo = valores.get(
        "vinculo"
    )

    vinculo = valores.get(
        "nmvinculo"
    )

    padrao = valores.get(
        "padrao"
    )

    data_admissao = converter_data(
        valores.get(
            "admissao"
        )
    )

    pensionista = converter_booleano(
        valores.get(
            "pensionista"
        )
    )

    inativo = converter_booleano(
        valores.get(
            "inativo"
        )
    )

    referencia_date = datetime.strptime(
        referencia,
        "%Y-%m-%d",
    ).date()

    ocorrencias_por_codigo = defaultdict(
        int
    )

    registros = []

    for detalhe in detalhes:
        codigo_rubrica = detalhe.get(
            "conta"
        )

        # conta = 0 representa linhas
        # agregadas da folha:
        #
        # Total Créditos
        # Total Débitos
        # Total Líquido
        #
        # Não são rubricas individuais.
        if not codigo_rubrica:
            continue

        codigo_rubrica = int(
            codigo_rubrica
        )

        ocorrencias_por_codigo[
            codigo_rubrica
        ] += 1

        sequencia_ocorrencia = (
            ocorrencias_por_codigo[
                codigo_rubrica
            ]
        )

        registros.append(
            (
                str(matricula),
                referencia_date,
                codigo_rubrica,
                sequencia_ocorrencia,
                detalhe.get(
                    "descricao"
                ),
                detalhe.get(
                    "colunaMviewRemuneracao"
                ),
                detalhe.get(
                    "sinal"
                ),
                detalhe.get(
                    "valor"
                ),
                nome_servidor,
                (
                    str(codigo_cargo)
                    if codigo_cargo
                    is not None
                    else None
                ),
                cargo,
                (
                    str(codigo_setor)
                    if codigo_setor
                    is not None
                    else None
                ),
                setor,
                (
                    str(codigo_orgao)
                    if codigo_orgao
                    is not None
                    else None
                ),
                orgao,
                (
                    str(codigo_vinculo)
                    if codigo_vinculo
                    is not None
                    else None
                ),
                vinculo,
                padrao,
                data_admissao,
                pensionista,
                inativo,
                endpoint_origem,
            )
        )

    return registros


def gravar_lote(
    conn,
    registros,
):
    if not registros:
        return

    sql = """
        INSERT INTO agora.fato_remuneracao_rubrica (
            matricula,
            referencia,
            codigo_rubrica,
            sequencia_ocorrencia,
            descricao_api,
            grupo_remuneratorio,
            sinal,
            valor,
            nome_servidor,
            codigo_cargo,
            cargo,
            codigo_setor,
            setor,
            codigo_orgao,
            orgao,
            codigo_vinculo,
            vinculo,
            padrao,
            data_admissao,
            pensionista,
            inativo,
            endpoint_origem
        )
        VALUES %s
        ON CONFLICT (
            matricula,
            referencia,
            codigo_rubrica,
            sequencia_ocorrencia
        )
        DO UPDATE SET
            descricao_api =
                EXCLUDED.descricao_api,

            grupo_remuneratorio =
                EXCLUDED.grupo_remuneratorio,

            sinal =
                EXCLUDED.sinal,

            valor =
                EXCLUDED.valor,

            nome_servidor =
                EXCLUDED.nome_servidor,

            codigo_cargo =
                EXCLUDED.codigo_cargo,

            cargo =
                EXCLUDED.cargo,

            codigo_setor =
                EXCLUDED.codigo_setor,

            setor =
                EXCLUDED.setor,

            codigo_orgao =
                EXCLUDED.codigo_orgao,

            orgao =
                EXCLUDED.orgao,

            codigo_vinculo =
                EXCLUDED.codigo_vinculo,

            vinculo =
                EXCLUDED.vinculo,

            padrao =
                EXCLUDED.padrao,

            data_admissao =
                EXCLUDED.data_admissao,

            pensionista =
                EXCLUDED.pensionista,

            inativo =
                EXCLUDED.inativo,

            endpoint_origem =
                EXCLUDED.endpoint_origem,

            data_carga =
                CURRENT_TIMESTAMP
    """

    try:
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                sql,
                registros,
                page_size=1000,
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise


def processar_servidor(
    servidor,
    referencia,
):
    matricula = str(
        servidor.get(
            "matricula"
        )
    )

    nome = (
        servidor.get(
            "nmfuncionario"
        )
        or ""
    )

    payload, endpoint_origem = (
        consultar_folha_worker(
            matricula=matricula,
            referencia=referencia,
        )
    )

    registros = transformar_folha_em_registros(
        matricula=matricula,
        referencia=referencia,
        payload=payload,
        endpoint_origem=endpoint_origem,
    )

    return {
        "matricula": matricula,
        "nome": nome,
        "registros": registros,
    }


def formatar_tempo(segundos):
    segundos = max(
        0,
        int(segundos),
    )

    horas = segundos // 3600

    minutos = (
        segundos % 3600
    ) // 60

    segundos = segundos % 60

    if horas:
        return (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

    return (
        f"{minutos:02d}:"
        f"{segundos:02d}"
    )


def executar_carga_completa():
    sessao_principal = None
    conn = None

    inicio_geral = time.time()

    total_folhas_processadas = 0
    total_folhas_puladas = 0
    total_rubricas_processadas = 0
    total_erros = 0

    erros = []

    try:
        print(
            "=" * 76
        )

        print(
            "ÁGORA — CARGA PARALELA "
            "DA FOLHA DETALHADA TJRR"
        )

        print(
            "Período: janeiro a junho de 2025"
        )

        print(
            f"Workers simultâneos: "
            f"{MAX_WORKERS}"
        )

        print(
            f"Tentativas por requisição: "
            f"{MAX_TENTATIVAS}"
        )

        print(
            "=" * 76
        )

        sessao_principal = (
            inicializar_sessao_principal()
        )

        conn = psycopg2.connect(
            **DB_PARAMS
        )

        for referencia in REFERENCIAS_CARGA:
            inicio_mes = time.time()

            print()
            print(
                "=" * 76
            )

            print(
                f"REFERÊNCIA "
                f"{referencia[5:7]}/"
                f"{referencia[0:4]}"
            )

            print(
                "=" * 76
            )

            print(
                "Obtendo relação de servidores..."
            )

            servidores = (
                listar_servidores_referencia(
                    sessao=sessao_principal,
                    referencia=referencia,
                )
            )

            ja_carregadas = (
                buscar_folhas_ja_carregadas(
                    conn=conn,
                    referencia=referencia,
                )
            )

            pendentes = []

            for servidor in servidores:
                matricula = str(
                    servidor.get(
                        "matricula"
                    )
                )

                if matricula in ja_carregadas:
                    continue

                pendentes.append(
                    servidor
                )

            total_mes = len(
                servidores
            )

            puladas_mes = (
                total_mes
                - len(pendentes)
            )

            total_folhas_puladas += (
                puladas_mes
            )

            print()
            print(
                "Matrículas no portal:",
                total_mes,
            )

            print(
                "Já carregadas:",
                puladas_mes,
            )

            print(
                "Pendentes:",
                len(
                    pendentes
                ),
            )

            if not pendentes:
                print(
                    "Referência já está completa."
                )

                continue

            buffer_registros = []

            folhas_no_buffer = 0

            concluidas_mes = 0
            rubricas_mes = 0
            erros_mes = 0

            with ThreadPoolExecutor(
                max_workers=MAX_WORKERS
            ) as executor:

                futuros = {
                    executor.submit(
                        processar_servidor,
                        servidor,
                        referencia,
                    ): servidor
                    for servidor in pendentes
                }

                total_pendentes = len(
                    futuros
                )

                for futuro in as_completed(
                    futuros
                ):
                    servidor = futuros[
                        futuro
                    ]

                    matricula = str(
                        servidor.get(
                            "matricula"
                        )
                    )

                    nome = (
                        servidor.get(
                            "nmfuncionario"
                        )
                        or ""
                    )

                    try:
                        resultado = futuro.result()

                        registros = resultado[
                            "registros"
                        ]

                        buffer_registros.extend(
                            registros
                        )

                        folhas_no_buffer += 1
                        concluidas_mes += 1

                        total_folhas_processadas += 1

                        rubricas_mes += len(
                            registros
                        )

                        total_rubricas_processadas += len(
                            registros
                        )

                        if (
                            folhas_no_buffer
                            >= TAMANHO_LOTE_FOLHAS
                        ):
                            gravar_lote(
                                conn=conn,
                                registros=buffer_registros,
                            )

                            buffer_registros = []
                            folhas_no_buffer = 0

                        decorridos = (
                            time.time()
                            - inicio_mes
                        )

                        processados = (
                            concluidas_mes
                            + erros_mes
                        )

                        velocidade = (
                            processados
                            / decorridos
                            if decorridos > 0
                            else 0
                        )

                        restantes = (
                            total_pendentes
                            - processados
                        )

                        eta = (
                            restantes
                            / velocidade
                            if velocidade > 0
                            else 0
                        )

                        if (
                            processados == 1
                            or processados % 25 == 0
                            or processados
                            == total_pendentes
                        ):
                            print(
                                f"  [{processados}/"
                                f"{total_pendentes}] "
                                f"OK | "
                                f"rubricas="
                                f"{rubricas_mes} | "
                                f"erros="
                                f"{erros_mes} | "
                                f"ETA="
                                f"{formatar_tempo(eta)}"
                            )

                    except Exception as erro:
                        erros_mes += 1
                        total_erros += 1

                        processados = (
                            concluidas_mes
                            + erros_mes
                        )

                        mensagem = (
                            f"{referencia} | "
                            f"{matricula} | "
                            f"{nome} | "
                            f"{type(erro).__name__}: "
                            f"{erro}"
                        )

                        erros.append(
                            mensagem
                        )

                        print(
                            "  ERRO:",
                            mensagem,
                        )

            if buffer_registros:
                gravar_lote(
                    conn=conn,
                    registros=buffer_registros,
                )

            duracao_mes = (
                time.time()
                - inicio_mes
            )

            print()
            print(
                f"{referencia[5:7]}/"
                f"{referencia[0:4]} "
                "concluído."
            )

            print(
                "  novas folhas:",
                concluidas_mes,
            )

            print(
                "  já existentes:",
                puladas_mes,
            )

            print(
                "  rubricas:",
                rubricas_mes,
            )

            print(
                "  erros:",
                erros_mes,
            )

            print(
                "  tempo:",
                formatar_tempo(
                    duracao_mes
                ),
            )

        duracao_geral = (
            time.time()
            - inicio_geral
        )

        print()
        print(
            "=" * 76
        )

        print(
            "CARGA COMPLETA FINALIZADA"
        )

        print(
            "=" * 76
        )

        print(
            "Novas folhas processadas:",
            total_folhas_processadas,
        )

        print(
            "Folhas já existentes/puladas:",
            total_folhas_puladas,
        )

        print(
            "Rubricas processadas:",
            total_rubricas_processadas,
        )

        print(
            "Erros:",
            total_erros,
        )

        print(
            "Tempo total:",
            formatar_tempo(
                duracao_geral
            ),
        )

        if erros:
            print()
            print(
                "ERROS ENCONTRADOS"
            )

            print(
                "-" * 76
            )

            for mensagem in erros:
                print(
                    mensagem
                )

        print(
            "=" * 76
        )

    finally:
        if conn is not None:
            conn.close()

        if sessao_principal is not None:
            sessao_principal.close()


if __name__ == "__main__":
    executar_carga_completa()
