import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "agora"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

TARGET_SCHEMA = "agora"

def extrair_estrutura():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    estrutura = {
        "database": DB_PARAMS["dbname"],
        "schema": TARGET_SCHEMA,
        "tables": []
    }

    tabelas_dict = {}

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
    """, (TARGET_SCHEMA,))
    
    for row in cursor.fetchall():
        nome = row['table_name']
        tabelas_dict[nome] = {
            "name": nome,
            "columns": [],
            "primary_key": [],
            "foreign_keys": []
        }

    cursor.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s
    """, (TARGET_SCHEMA,))
    
    for row in cursor.fetchall():
        tabela = row['table_name']
        if tabela in tabelas_dict:
            tabelas_dict[tabela]['columns'].append({
                "name": row['column_name'],
                "type": row['data_type'],
                "nullable": row['is_nullable'] == 'YES'
            })

    cursor.execute("""
        SELECT kcu.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
    """, (TARGET_SCHEMA,))
    
    for row in cursor.fetchall():
        tabela = row['table_name']
        if tabela in tabelas_dict:
            tabelas_dict[tabela]['primary_key'].append(row['column_name'])

    cursor.execute("""
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
    """, (TARGET_SCHEMA,))
    
    for row in cursor.fetchall():
        tabela = row['table_name']
        if tabela in tabelas_dict:
            tabelas_dict[tabela]['foreign_keys'].append({
                "column": row['column_name'],
                "references_table": row['foreign_table_name'],
                "references_column": row['foreign_column_name']
            })

    cursor.close()
    conn.close()
    
    estrutura["tables"] = list(tabelas_dict.values())
    
    return estrutura

if __name__ == "__main__":
    print("Iniciando extração do schema...")
    resultado_json = extrair_estrutura()
    
    caminho_arquivo = os.path.join(os.path.dirname(__file__), 'data_catalog.json')
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultado_json, f, indent=4, ensure_ascii=False)
        
    print(f"Sucesso! Estrutura salva em {caminho_arquivo}")