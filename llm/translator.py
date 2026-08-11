import os
import json
from providers import LLMProvider

class TradutorNL2SQL:
    def __init__(self, llm_provider: LLMProvider, nome_catalogo="data_catalog.example.json"):
        self.llm = llm_provider
        
        # Pega o diretório exato da pasta llm/ onde este script está
        self.diretorio_base = os.path.dirname(os.path.abspath(__file__))
        
        # Carrega os arquivos externos para a memória logo que a classe é instanciada
        self.catalogo_str = self._carregar_catalogo(nome_catalogo)
        self.system_prompt = self._carregar_system_prompt()

    def _carregar_catalogo(self, nome_arquivo):
        caminho_completo = os.path.join(self.diretorio_base, nome_arquivo)
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), indent=2, ensure_ascii=False)
        except FileNotFoundError:
            raise FileNotFoundError(f"Catálogo não encontrado: {caminho_completo}")

    def _carregar_system_prompt(self, caminho_relativo="prompts/system_prompt.md"):
        # Aponta para a subpasta prompts/ que está dentro de llm/
        caminho_completo = os.path.join(self.diretorio_base, caminho_relativo)
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de regras não encontrado: {caminho_completo}")

    def processar_pergunta(self, pergunta: str) -> dict:
        # Adicionamos uma exigência de formato JSON logo abaixo do system_prompt
        prompt_completo = f"""{self.system_prompt}

FORMATO DE SAÍDA OBRIGATÓRIO (JSON):
{{
  "status": "QUERY | NOT_ANSWERABLE | NEEDS_CLARIFICATION",
  "sql": "Comando SQL completo (apenas se status for QUERY)",
  "message": "Explicação (se status não for QUERY)"
}}

CATÁLOGO DE DADOS DISPONÍVEIS:
{self.catalogo_str}

PERGUNTA DO USUÁRIO:
{pergunta}
"""
        resposta_bruta = self.llm.gerar_sql(prompt_completo)
        json_limpo = resposta_bruta.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(json_limpo)
        except json.JSONDecodeError:
            return {
                "status": "NOT_ANSWERABLE",
                "message": "Erro interno ao processar a formatação da resposta da LLM."
            }