from pathlib import Path
from getpass import getpass
from datetime import date
import re
import unicodedata
from decimal import Decimal

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE = Path.home() / "agora" / "dados" / "tjrr"

PASTA_TLP = BASE / "tlp_2025"
PASTA_RUBRICAS = BASE / "rubricas"

ARQUIVO_RUBRICAS = (
    PASTA_RUBRICAS
    / "discriminacao_rubricas_folha_tjrr.ods"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "agora",
    "user": "postgres",
}

DATA_REFERENCIA_TLP = date(2025, 1, 1)


# ============================================================
# UTILITÁRIOS
# ============================================================

def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if not texto:
        return ""

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        c
        for c in texto
        if not unicodedata.combining(c)
    )

    texto = texto.upper()

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def texto_ou_none(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto in {
        "",
        "-",
        "NAN",
        "nan",
        "None",
    }:
        return None

    return texto


def inteiro_ou_zero(valor):
    if pd.isna(valor):
        return 0

    texto = str(valor).strip()

    if texto in {
        "",
        "-",
        "nan",
        "None",
    }:
        return 0

    try:
        return int(
            float(
                texto.replace(",", ".")
            )
        )
    except Exception:
        return 0


def descobrir_grupo(nome_arquivo):
    nome = normalizar_texto(
        nome_arquivo
    )

    if "TLP 1" in nome:
        return "TLP 1"

    if "TLP 2" in nome:
        return "TLP 2"

    if "TLP 3" in nome:
        return "TLP 3"

    raise ValueError(
        f"Grupo TLP não identificado: {nome_arquivo}"
    )


def descobrir_categoria_grupo(grupo):
    return {
        "TLP 1":
            "UNIDADES JUDICIÁRIAS DE PRIMEIRO E SEGUNDO GRAUS",

        "TLP 2":
            "UNIDADES DE APOIO DIRETO À ATIVIDADE JUDICANTE",

        "TLP 3":
            "UNIDADES DE APOIO INDIRETO À ATIVIDADE JUDICANTE",
    }[grupo]


# ============================================================
# LOCALIZAÇÃO DOS ARQUIVOS
# ============================================================

def localizar_arquivos_tlp():
    arquivos = sorted(
        PASTA_TLP.glob("*.ods")
    )

    nominais = []
    unidades = []

    for arquivo in arquivos:
        nome = normalizar_texto(
            arquivo.name
        )

        if (
            "RELACAO" in nome
            and "NOMINAL" in nome
        ):
            nominais.append(
                arquivo
            )
        else:
            unidades.append(
                arquivo
            )

    return nominais, unidades


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

DDL = """
CREATE SCHEMA IF NOT EXISTS agora;


-- =========================================================
-- SERVIDORES / VÍNCULOS DA TLP
-- =========================================================

CREATE TABLE IF NOT EXISTS agora.servidores_tlp (
    id BIGSERIAL PRIMARY KEY,

    data_referencia DATE NOT NULL,

    grupo_tlp VARCHAR(10) NOT NULL,

    categoria_tlp TEXT NOT NULL,

    numero INTEGER,

    matricula TEXT NOT NULL,

    nome TEXT NOT NULL,

    nome_normalizado TEXT,

    lotacao TEXT,

    origem_requisitado TEXT,

    cargo_efetivo TEXT,

    cargo_comissao TEXT,

    funcao_confianca TEXT,

    efetivo BOOLEAN NOT NULL DEFAULT FALSE,

    efetivo_com_cargo_comissao BOOLEAN
        NOT NULL DEFAULT FALSE,

    efetivo_com_funcao_confianca BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado_com_cargo_comissao BOOLEAN
        NOT NULL DEFAULT FALSE,

    requisitado_com_funcao_confianca BOOLEAN
        NOT NULL DEFAULT FALSE,

    exclusivamente_comissionado BOOLEAN
        NOT NULL DEFAULT FALSE,

    grau_jurisdicao TEXT,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE UNIQUE INDEX IF NOT EXISTS
    uq_servidores_tlp_referencia_matricula
ON agora.servidores_tlp (
    data_referencia,
    matricula
);


CREATE INDEX IF NOT EXISTS
    idx_servidores_tlp_nome_normalizado
ON agora.servidores_tlp (
    nome_normalizado
);


CREATE INDEX IF NOT EXISTS
    idx_servidores_tlp_grupo
ON agora.servidores_tlp (
    grupo_tlp
);


-- =========================================================
-- UNIDADES DA TLP
-- =========================================================

CREATE TABLE IF NOT EXISTS agora.unidades_tlp (
    id BIGSERIAL PRIMARY KEY,

    data_referencia DATE NOT NULL,

    grupo_tlp VARCHAR(10) NOT NULL,

    categoria_tlp TEXT NOT NULL,

    grau TEXT,

    tipo TEXT,

    unidade TEXT NOT NULL,

    uf TEXT,

    municipio_ibge TEXT,

    lotacao_paradigma INTEGER,

    lotacao_real_efetivos INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_requisitados INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_sem_vinculo INTEGER
        NOT NULL DEFAULT 0,

    lotacao_real_outros INTEGER
        NOT NULL DEFAULT 0,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
    idx_unidades_tlp_grupo
ON agora.unidades_tlp (
    grupo_tlp
);


CREATE INDEX IF NOT EXISTS
    idx_unidades_tlp_unidade
ON agora.unidades_tlp (
    unidade
);


-- =========================================================
-- CARGOS EM COMISSÃO / FUNÇÕES POR UNIDADE
-- =========================================================

CREATE TABLE IF NOT EXISTS
agora.unidades_tlp_cargos_funcoes (

    id BIGSERIAL PRIMARY KEY,

    unidade_tlp_id BIGINT NOT NULL
        REFERENCES agora.unidades_tlp(id)
        ON DELETE CASCADE,

    categoria TEXT NOT NULL
        CHECK (
            categoria IN (
                'CARGO_COMISSAO',
                'FUNCAO_CONFIANCA'
            )
        ),

    codigo TEXT,

    denominacao TEXT NOT NULL,

    quantidade INTEGER NOT NULL DEFAULT 0
);


CREATE INDEX IF NOT EXISTS
    idx_tlp_cargos_funcoes_unidade
ON agora.unidades_tlp_cargos_funcoes (
    unidade_tlp_id
);


-- =========================================================
-- RUBRICAS
-- =========================================================

CREATE TABLE IF NOT EXISTS agora.rubricas_folha (
    id BIGSERIAL PRIMARY KEY,

    codigo INTEGER NOT NULL UNIQUE,

    denominacao TEXT NOT NULL,

    fundamento_legal TEXT,

    arquivo_origem TEXT NOT NULL,

    data_carga TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
    idx_rubricas_denominacao
ON agora.rubricas_folha (
    denominacao
);
"""


# ============================================================
# TLP NOMINAL
# ============================================================

def ler_tlp_nominal(arquivo):
    grupo = descobrir_grupo(
        arquivo.name
    )

    categoria_tlp = (
        descobrir_categoria_grupo(
            grupo
        )
    )

    df = pd.read_excel(
        arquivo,
        sheet_name=0,
        header=None,
        engine="odf",
    )

    # Linha 0 = título
    # Linha 1 = cabeçalho
    # Linha 2 em diante = dados
    df = df.iloc[
        2:,
        :16,
    ].copy()

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
        "efetivo_cc",
        "efetivo_fc",
        "requisitado",
        "requisitado_cc",
        "requisitado_fc",
        "exclusivamente_comissionado",
        "grau_jurisdicao",
    ]

    df = df[
        df["nome"].notna()
        &
        df["matricula"].notna()
    ].copy()

    registros = []

    for _, row in df.iterrows():

        matricula = texto_ou_none(
            row["matricula"]
        )

        if matricula is None:
            continue

        matricula = re.sub(
            r"\.0$",
            "",
            matricula,
        )

        nome = texto_ou_none(
            row["nome"]
        )

        if nome is None:
            continue

        registros.append(
            (
                DATA_REFERENCIA_TLP,
                grupo,
                categoria_tlp,

                inteiro_ou_zero(
                    row["numero"]
                ),

                matricula,

                nome,

                normalizar_texto(
                    nome
                ),

                texto_ou_none(
                    row["lotacao"]
                ),

                texto_ou_none(
                    row["origem_requisitado"]
                ),

                texto_ou_none(
                    row["cargo_efetivo"]
                ),

                texto_ou_none(
                    row["cargo_comissao"]
                ),

                texto_ou_none(
                    row["funcao_confianca"]
                ),

                normalizar_texto(
                    row["efetivo"]
                ) == "X",

                normalizar_texto(
                    row["efetivo_cc"]
                ) == "X",

                normalizar_texto(
                    row["efetivo_fc"]
                ) == "X",

                normalizar_texto(
                    row["requisitado"]
                ) == "X",

                normalizar_texto(
                    row["requisitado_cc"]
                ) == "X",

                normalizar_texto(
                    row["requisitado_fc"]
                ) == "X",

                normalizar_texto(
                    row[
                        "exclusivamente_comissionado"
                    ]
                ) == "X",

                texto_ou_none(
                    row["grau_jurisdicao"]
                ),

                arquivo.name,
            )
        )

    return registros


# ============================================================
# TLP AGREGADA
# ============================================================

def ler_tlp_unidades(arquivo):
    grupo = descobrir_grupo(
        arquivo.name
    )

    categoria_tlp = (
        descobrir_categoria_grupo(
            grupo
        )
    )

    df = pd.read_excel(
        arquivo,
        sheet_name=0,
        header=None,
        engine="odf",
    )

    cabecalhos = [
        texto_ou_none(v)
        for v in df.iloc[4].tolist()
    ]

    codigos = [
        texto_ou_none(v)
        for v in df.iloc[3].tolist()
    ]

    # -----------------------------
    # Colunas-base por TLP
    # -----------------------------

    if grupo == "TLP 1":

        indices_base = {
            "grau": 0,
            "tipo": 1,
            "unidade": 2,
            "uf": 3,
            "municipio": 4,
            "lp": 5,
            "lr_efet": 6,
            "lr_i": 7,
            "lr_sv": 8,
        }

        primeiro_indice_cargo = 9

    else:

        indices_base = {
            "grau": 0,
            "tipo": None,
            "unidade": 1,
            "uf": 2,
            "municipio": 3,
            "lp": None,
            "lr_efet": 4,
            "lr_i": 5,
            "lr_sv": 6,
            "lr_outros": 7,
        }

        primeiro_indice_cargo = 8

    unidades = []

    # dados começam na linha 5
    for idx in range(
        5,
        len(df),
    ):

        row = df.iloc[idx]

        valor_primeira_coluna = (
            normalizar_texto(
                row.iloc[0]
            )
        )

        # Evita legenda / subtotal / rodapé
        if (
            not valor_primeira_coluna
            or valor_primeira_coluna.startswith(
                "LEGENDA"
            )
            or valor_primeira_coluna.startswith(
                "SUBTOTAIS"
            )
            or valor_primeira_coluna.startswith(
                "GRAU -"
            )
            or valor_primeira_coluna.startswith(
                "DSC_"
            )
            or valor_primeira_coluna.startswith(
                "UF -"
            )
            or valor_primeira_coluna.startswith(
                "MUNIC"
            )
            or valor_primeira_coluna.startswith(
                "LR_"
            )
            or valor_primeira_coluna.startswith(
                "CC -"
            )
            or valor_primeira_coluna.startswith(
                "FC -"
            )
        ):
            continue

        unidade = texto_ou_none(
            row.iloc[
                indices_base["unidade"]
            ]
        )

        if not unidade:
            continue

        grau = texto_ou_none(
            row.iloc[
                indices_base["grau"]
            ]
        )

        tipo = None

        if indices_base["tipo"] is not None:
            tipo = texto_ou_none(
                row.iloc[
                    indices_base["tipo"]
                ]
            )

        uf = texto_ou_none(
            row.iloc[
                indices_base["uf"]
            ]
        )

        municipio = texto_ou_none(
            row.iloc[
                indices_base["municipio"]
            ]
        )

        lp = None

        if indices_base["lp"] is not None:
            lp = inteiro_ou_zero(
                row.iloc[
                    indices_base["lp"]
                ]
            )

        lr_efet = inteiro_ou_zero(
            row.iloc[
                indices_base["lr_efet"]
            ]
        )

        lr_i = inteiro_ou_zero(
            row.iloc[
                indices_base["lr_i"]
            ]
        )

        lr_sv = inteiro_ou_zero(
            row.iloc[
                indices_base["lr_sv"]
            ]
        )

        lr_outros = 0

        if (
            "lr_outros"
            in indices_base
        ):
            lr_outros = inteiro_ou_zero(
                row.iloc[
                    indices_base[
                        "lr_outros"
                    ]
                ]
            )

        cargos_funcoes = []

        for col in range(
            primeiro_indice_cargo,
            len(cabecalhos),
        ):

            denominacao = (
                cabecalhos[col]
            )

            if not denominacao:
                continue

            quantidade = inteiro_ou_zero(
                row.iloc[col]
            )

            codigo = codigos[col]

            codigo_normalizado = (
                normalizar_texto(
                    codigo
                )
            )

            # Classificação pelo código CNJ/TJRR
            if "FC" in codigo_normalizado:
                categoria = (
                    "FUNCAO_CONFIANCA"
                )
            else:
                categoria = (
                    "CARGO_COMISSAO"
                )

            # Guardamos apenas posições que
            # realmente existem naquela unidade.
            if quantidade > 0:

                cargos_funcoes.append(
                    (
                        categoria,
                        codigo,
                        denominacao,
                        quantidade,
                    )
                )

        unidades.append(
            {
                "grupo_tlp": grupo,
                "categoria_tlp":
                    categoria_tlp,

                "grau": grau,
                "tipo": tipo,
                "unidade": unidade,
                "uf": uf,
                "municipio": municipio,

                "lotacao_paradigma": lp,

                "lr_efet": lr_efet,
                "lr_i": lr_i,
                "lr_sv": lr_sv,
                "lr_outros": lr_outros,

                "arquivo_origem":
                    arquivo.name,

                "cargos_funcoes":
                    cargos_funcoes,
            }
        )

    return unidades


# ============================================================
# RUBRICAS
# ============================================================

def ler_rubricas():
    df = pd.read_excel(
        ARQUIVO_RUBRICAS,
        sheet_name=0,
        header=None,
        engine="odf",
    )

    # linha zero é cabeçalho
    df = df.iloc[
        1:,
        :3,
    ].copy()

    registros = []

    atual = None

    for _, row in df.iterrows():

        codigo = row.iloc[0]
        denominacao = row.iloc[1]
        fundamento = row.iloc[2]

        if pd.notna(codigo):

            # fecha rubrica anterior
            if atual is not None:
                registros.append(
                    atual
                )

            try:
                codigo_int = int(
                    float(codigo)
                )
            except Exception:
                continue

            atual = {
                "codigo":
                    codigo_int,

                "denominacao":
                    texto_ou_none(
                        denominacao
                    ),

                "fundamentos": [],
            }

            fundamento_txt = (
                texto_ou_none(
                    fundamento
                )
            )

            if fundamento_txt:
                atual[
                    "fundamentos"
                ].append(
                    fundamento_txt
                )

        else:

            # linha de continuação do fundamento
            if atual is None:
                continue

            fundamento_txt = (
                texto_ou_none(
                    fundamento
                )
            )

            if fundamento_txt:
                atual[
                    "fundamentos"
                ].append(
                    fundamento_txt
                )

    if atual is not None:
        registros.append(
            atual
        )

    resultado = []

    for item in registros:

        fundamentos = []

        for texto in item[
            "fundamentos"
        ]:

            if texto not in fundamentos:
                fundamentos.append(
                    texto
                )

        fundamento_final = (
            "\n\n".join(
                fundamentos
            )
            if fundamentos
            else None
        )

        resultado.append(
            (
                item["codigo"],
                item["denominacao"],
                fundamento_final,
                ARQUIVO_RUBRICAS.name,
            )
        )

    return resultado


# ============================================================
# CARGA
# ============================================================

def main():

    print("=" * 80)
    print("ÁGORA")
    print("CARGA TLP + RUBRICAS TJRR")
    print("=" * 80)

    nominais, unidades_arquivos = (
        localizar_arquivos_tlp()
    )

    print()
    print(
        f"Arquivos nominais encontrados: "
        f"{len(nominais)}"
    )

    for arquivo in nominais:
        print(
            f"  - {arquivo.name}"
        )

    print()
    print(
        f"Arquivos de unidades encontrados: "
        f"{len(unidades_arquivos)}"
    )

    for arquivo in unidades_arquivos:
        print(
            f"  - {arquivo.name}"
        )

    if len(nominais) != 3:
        raise RuntimeError(
            "Esperados 3 arquivos nominais da TLP."
        )

    if len(unidades_arquivos) != 3:
        raise RuntimeError(
            "Esperados 3 arquivos agregados da TLP."
        )

    if not ARQUIVO_RUBRICAS.exists():
        raise FileNotFoundError(
            ARQUIVO_RUBRICAS
        )

    # ========================================================
    # LEITURA DOS ARQUIVOS
    # ========================================================

    servidores = []

    for arquivo in nominais:

        dados = ler_tlp_nominal(
            arquivo
        )

        print(
            f"{arquivo.name}: "
            f"{len(dados)} registros nominais"
        )

        servidores.extend(
            dados
        )

    unidades = []

    for arquivo in unidades_arquivos:

        dados = ler_tlp_unidades(
            arquivo
        )

        print(
            f"{arquivo.name}: "
            f"{len(dados)} unidades"
        )

        unidades.extend(
            dados
        )

    rubricas = ler_rubricas()

    print()
    print(
        f"Rubricas consolidadas: "
        f"{len(rubricas)}"
    )

    # ========================================================
    # CONEXÃO
    # ========================================================

    senha = getpass(
        "\nSenha do PostgreSQL: "
    )

    config = DB_CONFIG.copy()
    config["password"] = senha

    conn = psycopg2.connect(
        **config
    )

    try:

        with conn.cursor() as cur:

            # -----------------------------------------------
            # DDL
            # -----------------------------------------------

            print()
            print(
                "Criando/verificando tabelas..."
            )

            cur.execute(
                DDL
            )

            # -----------------------------------------------
            # LIMPA SOMENTE O RECORTE DESTE MVP
            # -----------------------------------------------

            cur.execute(
                """
                DELETE FROM
                    agora.unidades_tlp_cargos_funcoes
                WHERE unidade_tlp_id IN (
                    SELECT id
                    FROM agora.unidades_tlp
                    WHERE data_referencia = %s
                );
                """,
                (
                    DATA_REFERENCIA_TLP,
                ),
            )

            cur.execute(
                """
                DELETE FROM agora.unidades_tlp
                WHERE data_referencia = %s;
                """,
                (
                    DATA_REFERENCIA_TLP,
                ),
            )

            cur.execute(
                """
                DELETE FROM agora.servidores_tlp
                WHERE data_referencia = %s;
                """,
                (
                    DATA_REFERENCIA_TLP,
                ),
            )

            cur.execute(
                """
                DELETE FROM agora.rubricas_folha;
                """
            )

            # -----------------------------------------------
            # SERVIDORES TLP
            # -----------------------------------------------

            print(
                "Carregando servidores TLP..."
            )

            execute_values(
                cur,
                """
                INSERT INTO
                    agora.servidores_tlp
                (
                    data_referencia,
                    grupo_tlp,
                    categoria_tlp,
                    numero,
                    matricula,
                    nome,
                    nome_normalizado,
                    lotacao,
                    origem_requisitado,
                    cargo_efetivo,
                    cargo_comissao,
                    funcao_confianca,
                    efetivo,
                    efetivo_com_cargo_comissao,
                    efetivo_com_funcao_confianca,
                    requisitado,
                    requisitado_com_cargo_comissao,
                    requisitado_com_funcao_confianca,
                    exclusivamente_comissionado,
                    grau_jurisdicao,
                    arquivo_origem
                )
                VALUES %s
                """,
                servidores,
                page_size=500,
            )

            # -----------------------------------------------
            # UNIDADES + CARGOS/FUNÇÕES
            # -----------------------------------------------

            print(
                "Carregando unidades TLP..."
            )

            for unidade in unidades:

                cur.execute(
                    """
                    INSERT INTO agora.unidades_tlp
                    (
                        data_referencia,
                        grupo_tlp,
                        categoria_tlp,
                        grau,
                        tipo,
                        unidade,
                        uf,
                        municipio_ibge,
                        lotacao_paradigma,
                        lotacao_real_efetivos,
                        lotacao_real_requisitados,
                        lotacao_real_sem_vinculo,
                        lotacao_real_outros,
                        arquivo_origem
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s
                    )
                    RETURNING id;
                    """,
                    (
                        DATA_REFERENCIA_TLP,

                        unidade[
                            "grupo_tlp"
                        ],

                        unidade[
                            "categoria_tlp"
                        ],

                        unidade["grau"],
                        unidade["tipo"],
                        unidade["unidade"],
                        unidade["uf"],
                        unidade["municipio"],

                        unidade[
                            "lotacao_paradigma"
                        ],

                        unidade["lr_efet"],
                        unidade["lr_i"],
                        unidade["lr_sv"],
                        unidade["lr_outros"],

                        unidade[
                            "arquivo_origem"
                        ],
                    ),
                )

                unidade_id = (
                    cur.fetchone()[0]
                )

                itens = []

                for item in unidade[
                    "cargos_funcoes"
                ]:

                    categoria, codigo, denominacao, quantidade = item

                    itens.append(
                        (
                            unidade_id,
                            categoria,
                            codigo,
                            denominacao,
                            quantidade,
                        )
                    )

                if itens:

                    execute_values(
                        cur,
                        """
                        INSERT INTO
                        agora.unidades_tlp_cargos_funcoes
                        (
                            unidade_tlp_id,
                            categoria,
                            codigo,
                            denominacao,
                            quantidade
                        )
                        VALUES %s
                        """,
                        itens,
                        page_size=200,
                    )

            # -----------------------------------------------
            # RUBRICAS
            # -----------------------------------------------

            print(
                "Carregando rubricas..."
            )

            execute_values(
                cur,
                """
                INSERT INTO agora.rubricas_folha
                (
                    codigo,
                    denominacao,
                    fundamento_legal,
                    arquivo_origem
                )
                VALUES %s
                """,
                rubricas,
                page_size=500,
            )

        conn.commit()

        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        print()
        print("=" * 80)
        print("RESUMO FINAL NO POSTGRESQL")
        print("=" * 80)

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    grupo_tlp,
                    COUNT(*)
                FROM agora.servidores_tlp
                WHERE data_referencia = %s
                GROUP BY grupo_tlp
                ORDER BY grupo_tlp;
                """,
                (
                    DATA_REFERENCIA_TLP,
                ),
            )

            print()
            print(
                "SERVIDORES TLP:"
            )

            total_servidores = 0

            for grupo, quantidade in cur.fetchall():

                print(
                    f"{grupo}: {quantidade}"
                )

                total_servidores += (
                    quantidade
                )

            print(
                f"TOTAL: {total_servidores}"
            )

            cur.execute(
                """
                SELECT
                    grupo_tlp,
                    COUNT(*)
                FROM agora.unidades_tlp
                WHERE data_referencia = %s
                GROUP BY grupo_tlp
                ORDER BY grupo_tlp;
                """,
                (
                    DATA_REFERENCIA_TLP,
                ),
            )

            print()
            print(
                "UNIDADES TLP:"
            )

            total_unidades = 0

            for grupo, quantidade in cur.fetchall():

                print(
                    f"{grupo}: {quantidade}"
                )

                total_unidades += (
                    quantidade
                )

            print(
                f"TOTAL: {total_unidades}"
            )

            cur.execute(
                """
                SELECT
                    categoria,
                    COUNT(*) AS itens,
                    SUM(quantidade) AS quantidade_total
                FROM
                    agora.unidades_tlp_cargos_funcoes
                GROUP BY categoria
                ORDER BY categoria;
                """
            )

            print()
            print(
                "CARGOS / FUNÇÕES:"
            )

            for linha in cur.fetchall():
                print(
                    f"{linha[0]} | "
                    f"itens: {linha[1]} | "
                    f"quantidade: {linha[2]}"
                )

            cur.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT codigo)
                FROM agora.rubricas_folha;
                """
            )

            total, codigos = (
                cur.fetchone()
            )

            print()
            print(
                "RUBRICAS:"
            )

            print(
                f"Registros: {total}"
            )

            print(
                f"Códigos distintos: {codigos}"
            )

            cur.execute(
                """
                SELECT COUNT(*)
                FROM agora.servidores_tlp;
                """
            )

            servidores_banco = (
                cur.fetchone()[0]
            )

            print()
            print(
                "VALIDAÇÃO ESPERADA:"
            )

            print(
                f"Servidores TLP: "
                f"{servidores_banco}"
            )

            print(
                f"Rubricas: {total}"
            )

            if (
                servidores_banco == 1136
                and total == 194
                and codigos == 194
            ):

                print()
                print(
                    "✅ CARGA TLP + RUBRICAS "
                    "CONCLUÍDA COM SUCESSO."
                )

            else:

                print()
                print(
                    "⚠️ Carga concluída, "
                    "mas os totais precisam "
                    "ser conferidos."
                )

    except Exception:

        conn.rollback()

        print()
        print(
            "❌ ERRO. "
            "ROLLBACK EXECUTADO."
        )

        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()

