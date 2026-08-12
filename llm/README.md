# Módulo LLM do Ágora

Este módulo é responsável por transformar perguntas em linguagem natural em consultas SQL compatíveis com o PostgreSQL utilizado pelo MVP.

---

## Arquitetura do Código

O código foi modularizado para separar responsabilidades e facilitar a manutenção pela equipe:

* **`providers.py`:** Responsável por gerenciar a conexão com as APIs de Inteligência Artificial (ex: Google Gemini). Contém mecanismos de proteção que interceptam falhas de comunicação e limites de cota da API (Erro 429), retornando estados seguros para a interface.
* **`translator.py`:** Atua como o motor de regras de negócio. Ele carrega dinamicamente o catálogo de dados (`.json`) e as regras da aplicação (`system_prompt.md`), constrói o prompt, aciona a IA e garante a extração e validação do JSON de saída.
* **`api_client.py`:** Faz a comunicação HTTP (via rede) com a API principal do Ágora. É a camada responsável por empacotar a string SQL gerada e enviá-la com segurança para o banco de dados via POST.
* **`main.py`:** O orquestrador central. Ele inicia o terminal interativo, repassa as perguntas para o `translator.py`, recebe o resultado, avalia os status e chama o `api_client.py` caso um SQL válido tenha sido gerado, exibindo logs formatados de todo o fluxo.

---

## ⚙️ Configuração do Ambiente

Para que o módulo consiga se conectar à Inteligência Artificial, é necessário configurar a sua chave de API. Na raiz da pasta `llm`, crie um arquivo chamado **exatamente** `.env` com o seguinte formato:

```text
GEMINI_API_KEY=sua_chave_real_aqui_sem_aspas
```

Aqui está a versão consolidada e atualizada do seu `README.md`. Eu mesclei o conteúdo original da Issue com as novas seções de arquitetura, configuração do ambiente e execução.

Você pode copiar todo o bloco abaixo e substituir o conteúdo atual do arquivo `llm/README.md`:

---

## Configuração do Ambiente

Para que o módulo consiga se conectar à Inteligência Artificial, é necessário configurar a sua chave de API. Na raiz da pasta `llm`, crie um arquivo chamado **exatamente** `.env` com o seguinte formato:

```text
GEMINI_API_KEY=sua_chave_real_aqui_sem_aspas
```

---

## Como Executar e Testar

**1. Instalar as dependências:**
Certifique-se de estar na pasta `llm` e execute no terminal:

```bash
pip install -r requirements.txt
```

**2. Executar o fluxo interativo:**
Para digitar as perguntas e ver o módulo trabalhando e conectando com o banco:

```bash
python main.py
```

**3. Executar os testes automatizados (QA):**
No terminal, posicionado na pasta raiz do repositório (`agora`), digite o comando abaixo para rodar todos os cenários de validação via `pytest`:

```bash
pytest llm/tests/ -v
```

---

## Entradas

O módulo recebe:

1. uma pergunta em linguagem natural;


2. um catálogo de dados em JSON.



Durante o desenvolvimento inicial, utilizar:
`llm/data_catalog.example.json`

Quando o módulo de catálogo estiver concluído, esse arquivo será substituído pelo `data_catalog.json` gerado automaticamente.

---

## Prompt-base

Utilizar as regras definidas em:
`llm/prompts/system_prompt.md`

O módulo deve seguir os contratos registrados em:
`docs/contratos.md`

---

## Saídas possíveis

O resultado deve ser um JSON válido contendo um dos seguintes estados:

* `QUERY`

* `NOT_ANSWERABLE`

* `NEEDS_CLARIFICATION`


---

## Regras principais

* utilizar somente tabelas e colunas presentes no catálogo;


* não criar nomes de tabelas manualmente no código;


* não criar nomes de colunas manualmente no código;


* não inventar relacionamentos;


* não utilizar conhecimento externo para responder perguntas sobre os dados;


* não executar SQL diretamente no PostgreSQL;


* gerar apenas consultas de leitura.



---

## Testes iniciais mapeados

### Teste 1 — consulta simples

Pergunta: > Quantos registros de remuneração existem em janeiro de 2025?
Resultado esperado: `QUERY`
Resultado esperado no PostgreSQL: `1338`

### Teste 2 — agregação

Pergunta: > Qual foi o total de rendimento líquido em junho de 2025?
Resultado esperado: `QUERY`

### Teste 3 — informação inexistente

Pergunta: > Qual é a formação acadêmica dos servidores?
Resultado esperado: `NOT_ANSWERABLE`

### Teste 4 — pergunta ambígua

Pergunta: > Qual foi a maior remuneração?
Resultado esperado: `NEEDS_CLARIFICATION`

---

## Integração seguinte

Quando o status for:
`QUERY`

o campo:
`sql`

deverá ser enviado para:
`POST /query` da API do Ágora.

```
Fluxo:
Pergunta → catálogo → LLM → SQL → API → PostgreSQL → resultado → resposta final.
```