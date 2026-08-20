import os
import json

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "agora"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

TARGET_SCHEMA = os.getenv("DB_SCHEMA", "agora")

MAX_DISTINCT_VALUES = int(
    os.getenv("CATALOG_MAX_DISTINCT_VALUES", "20")
)

MAX_VALUE_LENGTH = int(
    os.getenv("CATALOG_MAX_VALUE_LENGTH", "120")
)


TIPOS_ELEGIVEIS_DOMINIO = {
    "text",
    "character varying",
    "character",
    "date",
}


TERMOS_BLOQUEADOS = {
    "nome",
    "cpf",
    "cnpj",
    "documento",
    "matricula",
    "email",
    "telefone",
    "celular",
    "endereco",
    "logradouro",
    "cep",
    "senha",
    "password",
    "token",
    "secret",
    "chave",
    "arquivo",
    "path",
    "url",
    "observacao",
    "fundamento",
}


def coluna_elegivel_para_dominio(coluna):
    """
    Decide se uma coluna pode receber enriquecimento semântico
    por meio de valores distintos.

    O objetivo é descobrir categorias e valores de referência
    de baixa cardinalidade sem incorporar identificadores
    pessoais ou textos livres ao catálogo.
    """

    nome_coluna = coluna["name"].lower()
    tipo_coluna = coluna["type"].lower()

    if tipo_coluna not in TIPOS_ELEGIVEIS_DOMINIO:
        return False

    for termo in TERMOS_BLOQUEADOS:
        if termo in nome_coluna:
            return False

    return True


def extrair_valores_distintos(
    cursor,
    objeto,
    coluna,
):
    """
    Obtém valores distintos de uma coluna elegível.

    Funciona tanto para tabelas quanto para views.

    A consulta busca no máximo MAX_DISTINCT_VALUES + 1.
    Se houver mais valores do que o limite configurado,
    a coluna é considerada de alta cardinalidade e nenhum
    domínio é incorporado ao catálogo.
    """

    consulta = sql.SQL(
        """
        SELECT DISTINCT {coluna} AS valor
        FROM {schema}.{objeto}
        WHERE {coluna} IS NOT NULL
        ORDER BY {coluna}
        LIMIT %s
        """
    ).format(
        coluna=sql.Identifier(coluna),
        schema=sql.Identifier(TARGET_SCHEMA),
        objeto=sql.Identifier(objeto),
    )

    cursor.execute(
        consulta,
        (MAX_DISTINCT_VALUES + 1,),
    )

    linhas = cursor.fetchall()

    if len(linhas) > MAX_DISTINCT_VALUES:
        return None

    valores = []

    for row in linhas:
        valor = row["valor"]

        if valor is None:
            continue

        valor = str(valor).strip()

        if not valor:
            continue

        if len(valor) > MAX_VALUE_LENGTH:
            return None

        valores.append(valor)

    if not valores:
        return None

    return valores


def enriquecer_catalogo(
    cursor,
    objetos_dict,
):
    """
    Acrescenta automaticamente 'distinct_values'
    às colunas elegíveis de baixa cardinalidade que
    passarem pelas regras de segurança.

    O enriquecimento é aplicado tanto a tabelas
    quanto a views catalogadas.
    """

    for nome_objeto, objeto in objetos_dict.items():
        for coluna in objeto["columns"]:

            if not coluna_elegivel_para_dominio(coluna):
                continue

            valores = extrair_valores_distintos(
                cursor=cursor,
                objeto=nome_objeto,
                coluna=coluna["name"],
            )

            if valores is not None:
                coluna["distinct_values"] = valores


def extrair_estrutura():
    conn = psycopg2.connect(**DB_PARAMS)

    try:
        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        estrutura = {
            "database": DB_PARAMS["dbname"],
            "schema": TARGET_SCHEMA,
            "tables": [],
        }

        objetos_dict = {}

        # ---------------------------------------------------------
        # OBJETOS CONSULTÁVEIS
        #
        # O catálogo inclui tanto tabelas físicas quanto views.
        # O núcleo não precisa conhecer previamente os nomes dos
        # objetos nem possuir regras específicas por domínio.
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type IN (
                  'BASE TABLE',
                  'VIEW'
              )
            ORDER BY
                table_type,
                table_name
            """,
            (TARGET_SCHEMA,),
        )

        for row in cursor.fetchall():
            nome = row["table_name"]
            tipo_banco = row["table_type"]

            if tipo_banco == "VIEW":
                tipo_objeto = "view"
            else:
                tipo_objeto = "table"

            objetos_dict[nome] = {
                "name": nome,
                "object_type": tipo_objeto,
                "columns": [],
                "primary_key": [],
                "foreign_keys": [],
            }

        # ---------------------------------------------------------
        # COLUNAS
        #
        # Mantém a ordem física/lógica das colunas do objeto.
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable,
                ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY
                table_name,
                ordinal_position
            """,
            (TARGET_SCHEMA,),
        )

        for row in cursor.fetchall():
            objeto = row["table_name"]

            if objeto in objetos_dict:
                objetos_dict[objeto]["columns"].append(
                    {
                        "name": row["column_name"],
                        "type": row["data_type"],
                        "nullable": (
                            row["is_nullable"] == "YES"
                        ),
                    }
                )

        # ---------------------------------------------------------
        # PRIMARY KEYS
        #
        # Views normalmente não possuem PK declarada.
        # Quando não houver, a lista permanece vazia.
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                kcu.table_name,
                kcu.column_name,
                kcu.ordinal_position
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s
            ORDER BY
                kcu.table_name,
                kcu.ordinal_position
            """,
            (TARGET_SCHEMA,),
        )

        for row in cursor.fetchall():
            objeto = row["table_name"]

            if objeto in objetos_dict:
                objetos_dict[objeto][
                    "primary_key"
                ].append(
                    row["column_name"]
                )

        # ---------------------------------------------------------
        # FOREIGN KEYS
        #
        # Views normalmente não possuem FKs declaradas.
        # Quando não houver, a lista permanece vazia.
        # ---------------------------------------------------------
        cursor.execute(
            """
            SELECT
                tc.table_name AS table_name,
                kcu.column_name AS column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s
            ORDER BY
                tc.table_name,
                kcu.column_name,
                ccu.table_name,
                ccu.column_name
            """,
            (TARGET_SCHEMA,),
        )

        for row in cursor.fetchall():
            objeto = row["table_name"]

            if objeto in objetos_dict:
                objetos_dict[objeto][
                    "foreign_keys"
                ].append(
                    {
                        "column": row["column_name"],
                        "references_table": (
                            row["foreign_table_name"]
                        ),
                        "references_column": (
                            row["foreign_column_name"]
                        ),
                    }
                )

        # ---------------------------------------------------------
        # ENRIQUECIMENTO SEMÂNTICO AUTOMÁTICO
        # ---------------------------------------------------------
        enriquecer_catalogo(
            cursor=cursor,
            objetos_dict=objetos_dict,
        )

        # ---------------------------------------------------------
        # COMPATIBILIDADE
        #
        # Mantemos a chave "tables" no JSON porque ela já é
        # consumida pelo restante do Ágora.
        #
        # Cada item agora informa também "object_type":
        # - table
        # - view
        #
        # Dessa forma não quebramos o contrato atual e, ao mesmo
        # tempo, o catálogo passa a representar views.
        # ---------------------------------------------------------
        estrutura["tables"] = list(
            objetos_dict.values()
        )

        return estrutura

    finally:
        conn.close()


if __name__ == "__main__":
    print(
        "Iniciando extração do schema..."
    )

    resultado_json = extrair_estrutura()

    caminho_arquivo = os.path.join(
        os.path.dirname(__file__),
        "data_catalog.json",
    )

    with open(
        caminho_arquivo,
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            resultado_json,
            arquivo,
            indent=4,
            ensure_ascii=False,
        )

    total_objetos = len(
        resultado_json.get(
            "tables",
            [],
        )
    )

    total_tabelas = sum(
        1
        for objeto in resultado_json.get(
            "tables",
            [],
        )
        if objeto.get("object_type") == "table"
    )

    total_views = sum(
        1
        for objeto in resultado_json.get(
            "tables",
            [],
        )
        if objeto.get("object_type") == "view"
    )

    print(
        f"Sucesso! Estrutura salva em "
        f"{caminho_arquivo}"
    )

    print(
        f"Objetos catalogados: {total_objetos} "
        f"({total_tabelas} tabelas, "
        f"{total_views} views)"
    )
