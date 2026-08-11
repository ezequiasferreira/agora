import json
import os
from api_client import executar_sql_na_api
from google import genai
from dotenv import load_dotenv # <--- Importa a função que lê o arquivo

# CLASSE BASE
class LLMProvider:
    def gerar_sql(self, prompt: str) -> str:
        raise NotImplementedError("As subclasses devem implementar este método")

# IMPLEMENTAÇÃO COM GEMINI (TEMPORÁRIO)
class GeminiLLM(LLMProvider):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def gerar_sql(self, prompt: str) -> str:
        try:
            interaction = self.client.interactions.create(
                model="gemini-3.5-flash", 
                input=prompt
            )
            return interaction.output_text
            
        except Exception as e:
            # Captura o erro e transforma em string para análise
            erro_str = str(e)
            
            # Se for um erro de limite de cota (Rate Limit / 429)
            if "429" in erro_str or "Quota exceeded" in erro_str:
                print("\n[Aviso] Limite da API gratuita atingido. Pausando para não quebrar o sistema.")
                # Retornamos uma string JSON "fake" que será lida perfeitamente pelo seu TradutorNL2SQL
                return """{
                  "status": "NOT_ANSWERABLE",
                  "message": "O sistema está processando muitos pedidos no momento (Limite de Cota). Por favor, aguarde alguns segundos e tente novamente."
                }"""
            
            # Para qualquer outro erro de rede ou de API genérico
            return f"""{{
              "status": "NOT_ANSWERABLE",
              "message": "Erro de comunicação com o motor de Inteligência Artificial."
            }}"""


# --- 3. COMPONENTE PRINCIPAL ---
class TradutorNL2SQL:
    def __init__(self, llm_provider, nome_catalogo="data_catalog.example.json"):
        self.llm = llm_provider
        # Agora lemos o catálogo provisório do Gabriel
        self.catalogo_str = self._carregar_arquivo_local(nome_catalogo)

    def _carregar_arquivo_local(self, nome_arquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(diretorio_atual, nome_arquivo)
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                if nome_arquivo.endswith('.json'):
                    return json.dumps(json.load(f), indent=2, ensure_ascii=False)
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_completo}")

    def processar_pergunta(self, pergunta: str):
        # Incorporando as regras do system_prompt.md
        prompt_template = f"""Você é um especialista em PostgreSQL.

CATÁLOGO DE DADOS DISPONÍVEIS:
{self.catalogo_str}

REGRAS OBRIGATÓRIAS:
- Use SOMENTE tabelas e colunas existentes no catálogo.
- Não invente tabelas, colunas ou relacionamentos.
- Gere apenas comandos SELECT (SQL PostgreSQL válido).
- Gere a consulta de forma SEGURA E PARAMETRIZADA (use $1, $2 para os valores).
- Retorne APENAS um objeto JSON válido, sem formatação markdown, com a seguinte estrutura:

{{
  "status": "QUERY | NOT_ANSWERABLE | NEEDS_CLARIFICATION",
  "query": "Comando SQL parametrizado (se status for QUERY)",
  "message": "Motivo/Explicação (se status for NOT_ANSWERABLE ou NEEDS_CLARIFICATION)"
}}

PERGUNTA DO USUÁRIO:
{pergunta}

JSON:"""

        resposta_bruta = self.llm.gerar_sql(prompt_template)
        json_limpo = resposta_bruta.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(json_limpo)
        except json.JSONDecodeError:
            return {
                "status": "NOT_ANSWERABLE",
                "message": f"Erro interno ao processar a resposta da LLM."
            }

# --- TESTANDO O CÓDIGO ---
if __name__ == "__main__":
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
            # Extraímos apenas a query e os params para enviar ao Gelson
            payload = {
                "query": resultado_llm.get("query"),
            }
            log_execucao["generated_sql"] = payload
            
            print(f"[{status}] Enviando POST /query para o banco...")
            resposta_api = executar_sql_na_api(payload)
            log_execucao["api_response"] = resposta_api
            
        elif status in ["NOT_ANSWERABLE", "NEEDS_CLARIFICATION"]:
            log_execucao["error"] = resultado_llm.get("message")
            print(f"[{status}] Retorno para o usuário: {log_execucao['error']}")

        print("\n--- LOG DE EXECUÇÃO ---")
        print(json.dumps(log_execucao, indent=2, ensure_ascii=False))
        print("-" * 50)