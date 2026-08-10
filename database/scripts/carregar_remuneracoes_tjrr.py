from pathlib import Path
from decimal import Decimal, InvalidOperation
from getpass import getpass
import re
import sys

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE = (
    Path.home()
    / "agora"
    / "dados"
    / "tjrr"
    / "remuneracoes_2025"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "agora",
    "user": "postgres",
}

ANO = 2025

COLUNAS = [
    "nome",
    "cargo",
    "lotacao",
    "remuneracao_paradigma",
    "vantagens_pessoais",
    "subsidio_funcao_cargo_comissao",
    "indenizacoes",
    "vantagens_eventuais",
    "gratificacoes",
    "total_creditos",
    "previdencia_publica",
    "imposto_renda",
    "descontos_diversos",
    "retencao_teto",
    "total_debitos",
    "rendimento_liquido",
    "remuneracao_orgao_origem",
    "diarias",
]

COLUNAS_NUMERICAS = COLUNAS[3:]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def extrair_mes(nome_arquivo: str):
    """
    Extrai o mês de arquivos como:
    cnj_01_2025.ods
    cnj012025.ods
    """

    padroes = [
        r"cnj[_-]?(0[1-9]|1[0-2])[_-]?2025",
        r"(0[1-9]|1[0-2])[_-]?2025",
    ]

    texto = nome_arquivo.lower()

    for padrao in padroes:
        match = re.search(padrao, texto)

        if match:
            return int(match.group(1))

    return None


def decimal_seguro(valor):
    """
    Converte valor para Decimal com duas casas.
    """

    if pd.isna(valor):
        return Decimal("0.00")

    try:
        return Decimal(str(valor)).quantize(
            Decimal("0.01")
        )
    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return Decimal("0.00")


def texto_seguro(valor):
    """
    Converte campos textuais, removendo NaN.
    """

    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    return texto


def carregar_arquivo_ods(arquivo: Path):
    """
    Lê a Plan1.

    Layout confirmado:
    linha 18 = cabeçalho superior
    linha 19 = cabeçalho inferior
    linha 20 em diante = dados
    """

    df = pd.read_excel(
        arquivo,
        sheet_name="Plan1",
        header=None,
        engine="odf",
    )

    # Registros começam na linha índice 20.
    df = df.iloc[20:, :18].copy()

    # Aplica nomes lógicos definidos no MVP.
    df.columns = COLUNAS

    # Remove linhas completamente vazias.
    df = df.dropna(
        how="all"
    )

    # Nome é essencial.
    df = df[
        df["nome"].notna()
    ]

    # Limpeza de texto.
    for coluna in [
        "nome",
        "cargo",
        "lotacao",
    ]:
        df[coluna] = (
            df[coluna]
            .apply(texto_seguro)
        )

    # Remove linhas cuja coluna nome ficou vazia.
    df = df[
        df["nome"].notna()
    ]

    # Conversão dos valores financeiros.
    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = (
            df[coluna]
            .apply(decimal_seguro)
        )

    return df


def conectar():
    """
    Abre conexão solicitando senha sem exibi-la.
    """

    senha = getpass(
        "Senha do usuário postgres: "
    )

    config = DB_CONFIG.copy()
    config["password"] = senha

    return psycopg2.connect(
        **config
    )


# ============================================================
# BANCO
# ============================================================

def apagar_competencia_existente(
    cursor,
    ano,
    mes,
):
    """
    Remove a competência antes da recarga.

    Torna o script idempotente:
    pode ser executado novamente sem duplicar dados.
    """

    cursor.execute(
        """
        DELETE FROM agora.remuneracoes
        WHERE ano = %s
          AND mes = %s
        """,
        (
            ano,
            mes,
        ),
    )

    return cursor.rowcount


def inserir_dados(
    cursor,
    df,
    ano,
    mes,
    arquivo,
):
    """
    Insere os registros em lote.
    """

    valores = []

    for _, linha in df.iterrows():

        valores.append(
            (
                ano,
                mes,

                linha["nome"],
                linha["cargo"],
                linha["lotacao"],

                linha["remuneracao_paradigma"],
                linha["vantagens_pessoais"],
                linha["subsidio_funcao_cargo_comissao"],
                linha["indenizacoes"],
                linha["vantagens_eventuais"],
                linha["gratificacoes"],
                linha["total_creditos"],

                linha["previdencia_publica"],
                linha["imposto_renda"],
                linha["descontos_diversos"],
                linha["retencao_teto"],
                linha["total_debitos"],

                linha["rendimento_liquido"],
                linha["remuneracao_orgao_origem"],
                linha["diarias"],

                arquivo.name,
            )
        )

    sql = """
        INSERT INTO agora.remuneracoes (
            ano,
            mes,

            nome,
            cargo,
            lotacao,

            remuneracao_paradigma,
            vantagens_pessoais,
            subsidio_funcao_cargo_comissao,
            indenizacoes,
            vantagens_eventuais,
            gratificacoes,
            total_creditos,

            previdencia_publica,
            imposto_renda,
            descontos_diversos,
            retencao_teto,
            total_debitos,

            rendimento_liquido,
            remuneracao_orgao_origem,
            diarias,

            arquivo_origem
        )
        VALUES %s
    """

    execute_values(
        cursor,
        sql,
        valores,
        page_size=1000,
    )

    return len(
        valores
    )


# ============================================================
# VALIDAÇÕES
# ============================================================

def validar_competencia(
    cursor,
    ano,
    mes,
):
    """
    Retorna contagem e totais básicos.
    """

    cursor.execute(
        """
        SELECT
            COUNT(*) AS quantidade,
            COALESCE(
                SUM(total_creditos),
                0
            ) AS total_creditos,
            COALESCE(
                SUM(total_debitos),
                0
            ) AS total_debitos,
            COALESCE(
                SUM(rendimento_liquido),
                0
            ) AS rendimento_liquido
        FROM agora.remuneracoes
        WHERE ano = %s
          AND mes = %s
        """,
        (
            ano,
            mes,
        ),
    )

    return cursor.fetchone()


def validar_semestre(
    cursor,
):
    """
    Mostra resumo final por mês.
    """

    cursor.execute(
        """
        SELECT
            mes,
            COUNT(*) AS registros,
            SUM(total_creditos) AS total_creditos,
            SUM(total_debitos) AS total_debitos,
            SUM(rendimento_liquido) AS rendimento_liquido
        FROM agora.remuneracoes
        WHERE ano = 2025
          AND mes BETWEEN 1 AND 6
        GROUP BY mes
        ORDER BY mes
        """
    )

    return cursor.fetchall()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("ÁGORA - CARGA DAS REMUNERAÇÕES TJRR")
    print("Período: janeiro a junho de 2025")
    print("=" * 80)

    arquivos = sorted(
        BASE.rglob(
            "cnj_*_2025.ods"
        )
    )

    if not arquivos:

        print(
            "\nERRO: nenhum arquivo ODS encontrado."
        )

        print(
            f"Pasta pesquisada: {BASE}"
        )

        sys.exit(1)

    print(
        f"\nArquivos encontrados: "
        f"{len(arquivos)}"
    )

    for arquivo in arquivos:
        print(
            f"  - {arquivo}"
        )

    if len(arquivos) != 6:

        print(
            "\nAVISO: eram esperados 6 arquivos."
        )

    try:
        conexao = conectar()

    except Exception as erro:

        print(
            f"\nERRO ao conectar ao PostgreSQL:"
            f"\n{erro}"
        )

        sys.exit(1)

    conexao.autocommit = False

    cursor = conexao.cursor()

    resultados = []

    try:

        for arquivo in arquivos:

            mes = extrair_mes(
                arquivo.name
            )

            if not mes:

                print(
                    f"\nIgnorando arquivo sem mês detectável: "
                    f"{arquivo.name}"
                )

                continue

            if mes < 1 or mes > 6:

                continue

            print("\n" + "-" * 80)

            print(
                f"Competência: "
                f"{mes:02d}/{ANO}"
            )

            print(
                f"Arquivo: "
                f"{arquivo.name}"
            )

            # --------------------------------------------
            # Leitura do ODS
            # --------------------------------------------

            df = carregar_arquivo_ods(
                arquivo
            )

            print(
                f"Registros válidos no ODS: "
                f"{len(df)}"
            )

            # --------------------------------------------
            # Remove eventual carga anterior
            # --------------------------------------------

            removidos = (
                apagar_competencia_existente(
                    cursor,
                    ANO,
                    mes,
                )
            )

            if removidos:

                print(
                    f"Registros antigos removidos: "
                    f"{removidos}"
                )

            # --------------------------------------------
            # Insere
            # --------------------------------------------

            inseridos = inserir_dados(
                cursor,
                df,
                ANO,
                mes,
                arquivo,
            )

            # --------------------------------------------
            # Valida antes do commit
            # --------------------------------------------

            (
                quantidade,
                total_creditos,
                total_debitos,
                rendimento_liquido,
            ) = validar_competencia(
                cursor,
                ANO,
                mes,
            )

            if quantidade != inseridos:

                raise RuntimeError(
                    f"Divergência na competência "
                    f"{mes:02d}/{ANO}: "
                    f"inseridos={inseridos}, "
                    f"banco={quantidade}"
                )

            conexao.commit()

            print(
                f"Registros inseridos: "
                f"{quantidade}"
            )

            print(
                f"Total de créditos: "
                f"R$ {total_creditos:,.2f}"
            )

            print(
                f"Total de débitos: "
                f"R$ {total_debitos:,.2f}"
            )

            print(
                f"Rendimento líquido: "
                f"R$ {rendimento_liquido:,.2f}"
            )

            resultados.append(
                (
                    mes,
                    quantidade,
                )
            )

        # ====================================================
        # RESUMO FINAL
        # ====================================================

        print("\n")
        print("=" * 80)
        print("RESUMO FINAL NO POSTGRESQL")
        print("=" * 80)

        resumo = validar_semestre(
            cursor
        )

        total_registros = 0

        for (
            mes,
            registros,
            creditos,
            debitos,
            liquido,
        ) in resumo:

            total_registros += registros

            print(
                f"\n{mes:02d}/2025"
            )

            print(
                f"  registros: "
                f"{registros}"
            )

            print(
                f"  créditos: "
                f"R$ {creditos:,.2f}"
            )

            print(
                f"  débitos: "
                f"R$ {debitos:,.2f}"
            )

            print(
                f"  líquido: "
                f"R$ {liquido:,.2f}"
            )

        print(
            "\n" + "-" * 80
        )

        print(
            f"TOTAL DE REGISTROS DO SEMESTRE: "
            f"{total_registros}"
        )

        # Verifica competências
        meses_carregados = {
            linha[0]
            for linha in resumo
        }

        faltantes = (
            set(range(1, 7))
            - meses_carregados
        )

        if faltantes:

            print(
                "ATENÇÃO - competências faltantes:"
            )

            for mes in sorted(
                faltantes
            ):

                print(
                    f"  {mes:02d}/2025"
                )

        else:

            print(
                "✅ PRIMEIRO SEMESTRE COMPLETO."
            )

        print(
            "\nCarga concluída com sucesso."
        )

    except Exception as erro:

        conexao.rollback()

        print(
            "\nERRO DURANTE A CARGA."
        )

        print(
            f"Rollback executado."
        )

        print(
            f"Detalhes: {erro}"
        )

        sys.exit(1)

    finally:

        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
