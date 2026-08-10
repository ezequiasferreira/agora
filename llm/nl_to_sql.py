import json
import os
from google import genai
from dotenv import load_dotenv # <--- Importa a função que lê o arquivo

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 2. Resgata a chave da memória
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")

# 3. CLASSE BASE
class LLMProvider:
    def gerar_sql(self, prompt: str) -> str:
        raise NotImplementedError("As subclasses devem implementar este método")

# 2. IMPLEMENTAÇÃO COM GEMINI
class GeminiLLM(LLMProvider):
    def __init__(self, api_key: str):
        # Inicializa o cliente passando a chave da API
        self.client = genai.Client(api_key=api_key)

    def gerar_sql(self, prompt: str) -> str:
        # Usando a estrutura da documentação que você enviou
        interaction = self.client.interactions.create(
            model="gemini-3.5-flash", 
            input=prompt
        )
        return interaction.output_text


# --- 3. COMPONENTE PRINCIPAL ---
class TradutorNL2SQL:
    def __init__(self, llm_provider: LLMProvider, caminho_schema: str = "schema_test.json"):
        self.llm = llm_provider
        self.schema_str = self._carregar_schema(caminho_schema)

    def _carregar_schema(self, nome_arquivo):
        # 1. Pega o diretório exato onde este script Python (.py) está salvo
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Junta o caminho do diretório com o nome do arquivo JSON
        caminho_completo = os.path.join(diretorio_atual, nome_arquivo)
        
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                schema_dict = json.load(f)
                return json.dumps(schema_dict, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado no caminho exato: {caminho_completo}")

    def processar_pergunta(self, pergunta: str) -> str:
        prompt_template = f"""Você é um especialista em banco de dados e atua como um tradutor de linguagem natural para SQL.

SCHEMA DO BANCO DE DADOS:
{self.schema_str}

REGRAS OBRIGATÓRIAS:
1. Retorne APENAS o código SQL válido. Não adicione formatação markdown (como ```sql), explicações, saudações ou comentários.
2. Se a pergunta não puder ser respondida, retorne: "UNANSWERABLE_QUESTION".

PERGUNTA DO USUÁRIO:
{pergunta}

SQL:"""

        resposta_bruta = self.llm.gerar_sql(prompt_template)
        sql_limpo = resposta_bruta.replace("```sql", "").replace("```", "").strip()
        return sql_limpo

# --- 4. TESTANDO O CÓDIGO ---
if __name__ == "__main__":

    # Se a chave não for encontrada, o programa avisa o erro de forma clara
    if not CHAVE_GEMINI:
        raise ValueError("Chave da API não encontrada. Verifique se o arquivo .env está configurado corretamente e contém GEMINI_API_KEY.")
    
    llm_escolhida = GeminiLLM(api_key=CHAVE_GEMINI)
    
    tradutor = TradutorNL2SQL(llm_provider=llm_escolhida)
    
    print("Módulo NL -> SQL iniciado. (Digite 'sair' para encerrar)")
    print("-" * 50)
    
    # Loop infinito para você fazer quantas perguntas quiser
    while True:
        # O programa pausa aqui e espera você digitar no terminal
        pergunta = input("\nDigite sua pergunta: ")
        
        # Condição para quebrar o loop e fechar o programa
        if pergunta.lower() in ['sair', 'exit', 'quit', '0']:
            print("Encerrando o módulo...")
            break
            
        # Ignora se você apertar Enter sem digitar nada
        if not pergunta.strip():
            continue
            
        print("Processando com a LLM...")
        resultado = tradutor.processar_pergunta(pergunta)
        
        print(f"SQL Gerado: \n{resultado}")
        print("-" * 50)