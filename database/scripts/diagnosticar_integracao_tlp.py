from pathlib import Path
from getpass import getpass
import re
import unicodedata

import pandas as pd
import psycopg2


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_TLP = (
    Path.home()
    / "agora"
    / "dados"
    / "tjrr"
    / "tlp_2025"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "agora",
    "user": "postgres",
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(valor):
    """
    Normalização APENAS para diagnóstico de correspondência.

    Não altera os dados originais.
    """

    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


# ============================================================
# IDENTIFICAÇÃO DOS ARQUIVOS NOMINAIS
# ============================================================

def localizar_relacoes_nominais():

    arquivos = sorted(
        BASE_TLP.glob("*.ods")
    )

    nominais = [
        arquivo
        for arquivo in arquivos
        if "RELA" in normalizar_texto(
            arquivo.name
        )
        and "NOMINAL" in normalizar_texto(
            arquivo.name
        )
    ]

    return nominais


# ============================================================
# LEITURA DA TLP
# ============================================================

def ler_relacao_nominal(arquivo):

    print()
    print(
        f"Lendo: {arquivo.name}"
    )

    df = pd.read_excel(
        arquivo,
        sheet_name=0,
        header=1,
        engine="odf",
    )

    # Mantemos as 16 colunas observadas
    # nos arquivos oficiais da TLP.
    df = df.iloc[:, :16].copy()

    df.columns = [
        "numero",
        "matricula",
        "nome",
        "lotacao",
        "origem_requisitado",
        "cargo_efetivo",
        "cargo_comissao",
        "funcao_confianca",
        "efetivo",
        "efetivo_com_cargo_comissao",
        "efetivo_com_funcao_confianca",
        "requisitado",
        "requisitado_com_cargo_comissao",
        "requisitado_com_funcao_confianca",
        "exclusivamente_comissionado",
        "grau_jurisdicao",
    ]

    # Descobre TLP 1, 2 ou 3 pelo nome
    nome_arquivo = normalizar_texto(
        arquivo.name
    )

    if "TLP 1" in nome_arquivo:
        grupo = "TLP 1"
    elif "TLP 2" in nome_arquivo:
        grupo = "TLP 2"
    elif "TLP 3" in nome_arquivo:
        grupo = "TLP 3"
    else:
        grupo = "TLP NÃO IDENTIFICADA"

    df["grupo_tlp"] = grupo
    df["arquivo_origem"] = arquivo.name

    # Remove linhas sem matrícula/nome
    df = df[
        df["nome"].notna()
    ].copy()

    df["nome"] = (
        df["nome"]
        .astype(str)
        .str.strip()
    )

    df["nome_normalizado"] = (
        df["nome"]
        .apply(normalizar_texto)
    )

    df["lotacao_normalizada"] = (
        df["lotacao"]
        .apply(normalizar_texto)
    )

    # matrícula como texto
    df["matricula"] = (
        df["matricula"]
        .astype(str)
        .str.replace(
            r"\.0$",
            "",
            regex=True,
        )
        .str.strip()
    )

    print(
        f"Registros úteis: {len(df)}"
    )

    return df


# ============================================================
# CARREGA REMUNERAÇÃO DO POSTGRESQL
# ============================================================

def carregar_remuneracoes():

    senha = getpass(
        "Senha do PostgreSQL: "
    )

    config = DB_CONFIG.copy()
    config["password"] = senha

    conn = psycopg2.connect(
        **config
    )

    sql = """
        SELECT
            id,
            ano,
            mes,
            nome,
            cargo,
            lotacao,
            total_creditos,
            total_debitos,
            rendimento_liquido,
            arquivo_origem
        FROM agora.remuneracoes
        WHERE ano = 2025
          AND mes BETWEEN 1 AND 6
        ORDER BY mes, nome;
    """

    df = pd.read_sql_query(
        sql,
        conn,
    )

    conn.close()

    df["nome_normalizado"] = (
        df["nome"]
        .apply(normalizar_texto)
    )

    df["lotacao_normalizada"] = (
        df["lotacao"]
        .apply(normalizar_texto)
    )

    return df


# ============================================================
# DIAGNÓSTICO
# ============================================================

def main():

    print("=" * 80)
    print("ÁGORA")
    print("DIAGNÓSTICO DE INTEGRAÇÃO")
    print("TLP 01/01/2025 × REMUNERAÇÕES 1º SEMESTRE/2025")
    print("=" * 80)

    # --------------------------------------------------------
    # 1. LOCALIZA OS 3 ARQUIVOS NOMINAIS
    # --------------------------------------------------------

    arquivos = localizar_relacoes_nominais()

    print()
    print(
        f"Relações nominais encontradas: "
        f"{len(arquivos)}"
    )

    for arquivo in arquivos:
        print(
            f" - {arquivo.name}"
        )

    if len(arquivos) != 3:

        print()
        print(
            "ATENÇÃO: esperávamos exatamente "
            "3 relações nominais."
        )

        print(
            f"Pasta analisada: {BASE_TLP}"
        )

        return

    # --------------------------------------------------------
    # 2. CONSOLIDA TLP
    # --------------------------------------------------------

    frames = [
        ler_relacao_nominal(
            arquivo
        )
        for arquivo in arquivos
    ]

    tlp = pd.concat(
        frames,
        ignore_index=True,
    )

    # --------------------------------------------------------
    # 3. CARREGA REMUNERAÇÃO
    # --------------------------------------------------------

    print()
    print(
        "Carregando remunerações do PostgreSQL..."
    )

    rem = carregar_remuneracoes()

    print(
        f"Registros de remuneração: "
        f"{len(rem)}"
    )

    # --------------------------------------------------------
    # 4. ESTATÍSTICAS DA TLP
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("TLP CONSOLIDADA")
    print("=" * 80)

    print(
        f"Registros funcionais: {len(tlp)}"
    )

    print(
        f"Matrículas distintas: "
        f"{tlp['matricula'].nunique()}"
    )

    print(
        f"Nomes distintos: "
        f"{tlp['nome_normalizado'].nunique()}"
    )

    print()
    print("Por grupo:")

    print(
        tlp
        .groupby("grupo_tlp")
        .size()
        .to_string()
    )

    # --------------------------------------------------------
    # 5. DUPLICIDADES
    # --------------------------------------------------------

    matriculas_duplicadas = (
        tlp
        .groupby("matricula")
        .size()
        .reset_index(
            name="quantidade"
        )
    )

    matriculas_duplicadas = (
        matriculas_duplicadas[
            matriculas_duplicadas[
                "quantidade"
            ] > 1
        ]
    )

    nomes_multiplas_matriculas = (
        tlp
        .groupby(
            [
                "nome_normalizado",
                "nome",
            ]
        )["matricula"]
        .nunique()
        .reset_index(
            name="quantidade_matriculas"
        )
    )

    nomes_multiplas_matriculas = (
        nomes_multiplas_matriculas[
            nomes_multiplas_matriculas[
                "quantidade_matriculas"
            ] > 1
        ]
    )

    print()
    print("=" * 80)
    print("DUPLICIDADES / MÚLTIPLOS VÍNCULOS")
    print("=" * 80)

    print(
        f"Matrículas repetidas: "
        f"{len(matriculas_duplicadas)}"
    )

    print(
        f"Pessoas com mais de uma matrícula: "
        f"{len(nomes_multiplas_matriculas)}"
    )

    # --------------------------------------------------------
    # 6. CRIA CONJUNTOS DE NOMES
    # --------------------------------------------------------

    nomes_tlp = set(
        tlp["nome_normalizado"]
    )

    nomes_rem = set(
        rem["nome_normalizado"]
    )

    nomes_tlp.discard("")
    nomes_rem.discard("")

    encontrados = (
        nomes_tlp
        & nomes_rem
    )

    apenas_tlp = (
        nomes_tlp
        - nomes_rem
    )

    apenas_rem = (
        nomes_rem
        - nomes_tlp
    )

    # --------------------------------------------------------
    # 7. COBERTURA GLOBAL
    # --------------------------------------------------------

    cobertura_tlp = (
        len(encontrados)
        / len(nomes_tlp)
        * 100
        if nomes_tlp
        else 0
    )

    cobertura_rem = (
        len(encontrados)
        / len(nomes_rem)
        * 100
        if nomes_rem
        else 0
    )

    print()
    print("=" * 80)
    print("CORRESPONDÊNCIA POR NOME NORMALIZADO")
    print("=" * 80)

    print(
        f"Nomes distintos na TLP: "
        f"{len(nomes_tlp)}"
    )

    print(
        f"Nomes distintos na remuneração: "
        f"{len(nomes_rem)}"
    )

    print(
        f"Correspondências: "
        f"{len(encontrados)}"
    )

    print(
        f"TLP encontrada na remuneração: "
        f"{cobertura_tlp:.2f}%"
    )

    print(
        f"Remuneração encontrada na TLP: "
        f"{cobertura_rem:.2f}%"
    )

    print(
        f"Nomes apenas na TLP: "
        f"{len(apenas_tlp)}"
    )

    print(
        f"Nomes apenas na remuneração: "
        f"{len(apenas_rem)}"
    )

    # --------------------------------------------------------
    # 8. COBERTURA POR MÊS
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("COBERTURA POR MÊS")
    print("=" * 80)

    resultados_mes = []

    for mes in range(1, 7):

        rem_mes = rem[
            rem["mes"] == mes
        ].copy()

        nomes_mes = set(
            rem_mes[
                "nome_normalizado"
            ]
        )

        nomes_mes.discard("")

        comuns = (
            nomes_tlp
            & nomes_mes
        )

        percentual = (
            len(comuns)
            / len(nomes_mes)
            * 100
            if nomes_mes
            else 0
        )

        resultados_mes.append(
            {
                "mes": mes,
                "nomes_remuneracao": len(
                    nomes_mes
                ),
                "nomes_encontrados_tlp": len(
                    comuns
                ),
                "percentual": percentual,
            }
        )

        print(
            f"{mes:02d}/2025 | "
            f"remuneração: {len(nomes_mes):4d} | "
            f"na TLP: {len(comuns):4d} | "
            f"{percentual:6.2f}%"
        )

    cobertura_mes = pd.DataFrame(
        resultados_mes
    )

    # --------------------------------------------------------
    # 9. ANALISA LOTAÇÃO DOS NOMES ENCONTRADOS
    # --------------------------------------------------------

    tlp_join = (
        tlp[
            [
                "nome",
                "nome_normalizado",
                "matricula",
                "grupo_tlp",
                "lotacao",
                "lotacao_normalizada",
                "cargo_efetivo",
                "cargo_comissao",
                "funcao_confianca",
                "origem_requisitado",
                "grau_jurisdicao",
            ]
        ]
        .copy()
    )

    rem_join = (
        rem[
            [
                "id",
                "ano",
                "mes",
                "nome",
                "nome_normalizado",
                "cargo",
                "lotacao",
                "lotacao_normalizada",
                "total_creditos",
                "total_debitos",
                "rendimento_liquido",
            ]
        ]
        .copy()
    )

    cruzamento = rem_join.merge(
        tlp_join,
        on="nome_normalizado",
        how="left",
        suffixes=(
            "_remuneracao",
            "_tlp",
        ),
    )

    cruzamento[
        "lotacao_exatamente_igual"
    ] = (
        cruzamento[
            "lotacao_normalizada_remuneracao"
        ]
        ==
        cruzamento[
            "lotacao_normalizada_tlp"
        ]
    )

    # --------------------------------------------------------
    # 10. PREPARA RELATÓRIOS
    # --------------------------------------------------------

    pasta_saida = (
        Path.home()
        / "agora"
        / "reports"
        / "integracao_tlp"
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    tlp.to_csv(
        pasta_saida
        / "tlp_consolidada.csv",
        index=False,
        encoding="utf-8-sig",
    )

    cobertura_mes.to_csv(
        pasta_saida
        / "cobertura_por_mes.csv",
        index=False,
        encoding="utf-8-sig",
    )

    nomes_apenas_tlp = (
        tlp[
            tlp["nome_normalizado"]
            .isin(apenas_tlp)
        ][
            [
                "matricula",
                "nome",
                "grupo_tlp",
                "lotacao",
                "cargo_efetivo",
                "cargo_comissao",
                "funcao_confianca",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "nome"
        )
    )

    nomes_apenas_tlp.to_csv(
        pasta_saida
        / "nomes_apenas_tlp.csv",
        index=False,
        encoding="utf-8-sig",
    )

    nomes_apenas_rem = (
        rem[
            rem["nome_normalizado"]
            .isin(apenas_rem)
        ][
            [
                "nome",
                "cargo",
                "lotacao",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "nome"
        )
    )

    nomes_apenas_rem.to_csv(
        pasta_saida
        / "nomes_apenas_remuneracao.csv",
        index=False,
        encoding="utf-8-sig",
    )

    nomes_multiplas_matriculas.to_csv(
        pasta_saida
        / "nomes_multiplas_matriculas.csv",
        index=False,
        encoding="utf-8-sig",
    )

    cruzamento.to_csv(
        pasta_saida
        / "cruzamento_tlp_remuneracao.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # 11. RESUMO FINAL
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("RESUMO FINAL")
    print("=" * 80)

    print(
        f"TLP - registros funcionais: "
        f"{len(tlp)}"
    )

    print(
        f"TLP - nomes distintos: "
        f"{len(nomes_tlp)}"
    )

    print(
        f"TLP - matrículas distintas: "
        f"{tlp['matricula'].nunique()}"
    )

    print(
        f"Remuneração - nomes distintos: "
        f"{len(nomes_rem)}"
    )

    print(
        f"Correspondências por nome: "
        f"{len(encontrados)}"
    )

    print(
        f"Cobertura TLP → remuneração: "
        f"{cobertura_tlp:.2f}%"
    )

    print(
        f"Cobertura remuneração → TLP: "
        f"{cobertura_rem:.2f}%"
    )

    print(
        f"Pessoas com múltiplas matrículas: "
        f"{len(nomes_multiplas_matriculas)}"
    )

    print()
    print(
        "Relatórios gravados em:"
    )

    print(
        pasta_saida
    )

    print()
    print(
        "✅ Diagnóstico concluído."
    )


if __name__ == "__main__":
    main()
