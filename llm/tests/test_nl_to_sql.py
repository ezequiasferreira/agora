import os
import sys
import pytest
from dotenv import load_dotenv

# Esse truque adiciona a pasta 'llm' (pai da pasta 'tests') no radar do Python
# Assim ele consegue encontrar o providers.py e translator.py sem dar erro de módulo
diretorio_llm = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, diretorio_llm)

# Agora importamos diretamente pelo nome do arquivo
from providers import GeminiLLM
from translator import TradutorNL2SQL

# Carrega a chave da API para os testes
load_dotenv()
CHAVE_GEMINI = os.getenv("GEMINI_API_KEY")

@pytest.fixture(scope="module")
def tradutor():
    """
    Esta 'fixture' inicializa o tradutor apenas uma vez e reaproveita 
    a mesma conexão em todos os 5 testes, deixando o processo rápido.
    """
    if not CHAVE_GEMINI:
        pytest.skip("Chave GEMINI_API_KEY não encontrada. Pulando testes.")
    
    llm = GeminiLLM(api_key=CHAVE_GEMINI)
    # Inicializa o tradutor (ele vai ler o json e o .md automaticamente)
    return TradutorNL2SQL(llm_provider=llm)


# --- OS 5 TESTES OFICIAIS DA ISSUE ---

def test_deve_retornar_query_para_contagem_simples(tradutor):
    pergunta = "Quantos registros de remuneração existem em janeiro de 2025?"
    resultado = tradutor.processar_pergunta(pergunta)
    
    assert resultado.get("status") == "QUERY", f"Esperado QUERY, mas retornou {resultado}"
    assert "sql" in resultado, "A chave 'sql' está faltando na resposta."
    assert "SELECT" in resultado.get("sql", "").upper(), "O SQL gerado é inválido."

def test_deve_retornar_query_para_agregacao(tradutor):
    pergunta = "Qual foi o total de rendimento líquido em junho de 2025?"
    resultado = tradutor.processar_pergunta(pergunta)
    
    assert resultado.get("status") == "QUERY", f"Esperado QUERY, mas retornou {resultado}"

def test_deve_retornar_query_para_dados_da_tlp(tradutor):
    pergunta = "Quantos servidores pertencem às unidades judiciárias de primeiro e segundo graus?"
    resultado = tradutor.processar_pergunta(pergunta)
    
    assert resultado.get("status") == "QUERY", f"Esperado QUERY, mas retornou {resultado}"

def test_deve_retornar_not_answerable_para_limitacao_de_dados(tradutor):
    pergunta = "Qual é a formação acadêmica dos servidores?"
    resultado = tradutor.processar_pergunta(pergunta)
    
    assert resultado.get("status") == "NOT_ANSWERABLE", f"Esperado NOT_ANSWERABLE, mas retornou {resultado}"
    assert resultado.get("message") is not None, "A mensagem de erro está faltando."

def test_deve_retornar_needs_clarification_para_ambiguidade(tradutor):
    pergunta = "Qual foi a maior remuneração?"
    resultado = tradutor.processar_pergunta(pergunta)
    
    assert resultado.get("status") == "NEEDS_CLARIFICATION", f"Esperado NEEDS_CLARIFICATION, mas retornou {resultado}"
    assert resultado.get("message") is not None, "A mensagem de esclarecimento está faltando."