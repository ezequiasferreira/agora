from google import genai

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
                # Retorna um JSON padronizado para que o restante da aplicação possa tratar o erro da mesma forma que trata uma resposta da LLM.
                return """{
                  "status": "NOT_ANSWERABLE",
                  "message": "O sistema está processando muitos pedidos no momento (Limite de Cota). Por favor, aguarde alguns segundos e tente novamente."
                }"""
            
            # Para qualquer outro erro de rede ou de API genérico
            return f"""{{
              "status": "NOT_ANSWERABLE",
              "message": "Erro de comunicação com o motor de Inteligência Artificial."
            }}"""