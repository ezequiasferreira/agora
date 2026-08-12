import requests

def executar_sql_na_api(sql_gerado: str):
    # Rota definida no FastAPI do Gelson
    url_api = "http://localhost:8000/query" 
    
    # Payload ajustado para bater com o QueryRequest e o Swagger
    payload = {
        "sql": sql_gerado
    }
    
    print(f"[Rede] Preparando envio para {url_api}...")
    
    try:
        # Envia a requisição POST para a API
        response = requests.post(url_api, json=payload)
        
        # O Gelson configurou retornos 400, 500 e 504 para erros
        if response.status_code != 200:
            print(f"[Erro da API] Status {response.status_code}: {response.json()}")
            return None
            
        # Retorna o dicionário com rows, columns, etc.
        return response.json()
        
    except requests.exceptions.RequestException as erro_rede:
        print(f"[Erro de Conexão] Falha ao comunicar com a API: {erro_rede}")
        return None