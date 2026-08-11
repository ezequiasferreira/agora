import os
import json
from dotenv import load_dotenv
from providers import GeminiLLM
from translator import TradutorNL2SQL
from api_client import executar_sql_na_api

load_dotenv()
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")

if not CHAVE_GEMINI:
    raise ValueError("Chave da API não encontrada no .env.")

tradutor = TradutorNL2SQL(llm_provider=GeminiLLM(api_key=CHAVE_GEMINI))

print("Módulo NL -> SQL (Projeto Ágora) iniciado. Digite 'sair' para encerrar.")
print("-" * 50)

while True:
    pergunta = input("\nDigite sua pergunta: ")
    
    if pergunta.lower() in ['sair', 'exit', 'quit', '0']:
        break
    if not pergunta.strip():
        continue
        
    # Log exigido pela documentação
    log_execucao = {
        "question": pergunta,
        "status_llm": None,
        "generated_sql": None,
        "api_response": None,
        "error": None
    }
    
    print("Processando com a LLM...")
    resultado_llm = tradutor.processar_pergunta(pergunta)
    
    status = resultado_llm.get("status")
    log_execucao["status_llm"] = status

    if status == "QUERY":
            # Agora buscamos a chave "sql" em vez de "query"
            query_string = resultado_llm.get("sql")
            
            # Trava de segurança: se mesmo assim vier vazio, avisamos o erro
            if not query_string:
                log_execucao["error"] = "A LLM gerou status QUERY, mas a string do SQL veio vazia."
                print("[Erro] Falha ao extrair a instrução SQL do JSON gerado.")
            else:
                log_execucao["generated_sql"] = query_string
                print(f"[{status}] Enviando POST /query para o banco...")
                
                # Passa a string do SQL diretamente para a nossa função de rede
                resposta_api = executar_sql_na_api(query_string) 
                log_execucao["api_response"] = resposta_api
        
    elif status in ["NOT_ANSWERABLE", "NEEDS_CLARIFICATION"]:
        log_execucao["error"] = resultado_llm.get("message")
        print(f"[{status}] Retorno para o usuário: {log_execucao['error']}")

    print("\n--- LOG DE EXECUÇÃO ---")
    print(json.dumps(log_execucao, indent=2, ensure_ascii=False))
    print("-" * 50)