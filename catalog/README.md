=========================================
EXTRATOR AUTOMÁTICO DO BANCO (ÁGORA)
=========================================

Este módulo é responsável por fazer a introspecção automática da estrutura do banco PostgreSQL utilizado pelo MVP do Ágora e gerar o catálogo de dados (data_catalog.json), sem depender de definições manuais no código.

--- PRÉ-REQUISITOS ---

- Python 3.x
- Banco de dados PostgreSQL contendo o database e schema 'agora'.
- Arquivo '.dump' do MVP restaurado localmente.

--- CONFIGURAÇÃO DO AMBIENTE ---

1. Instale as dependências necessárias para conectar ao banco e ler as variáveis de ambiente:
   pip install psycopg2-binary python-dotenv

2. Configure as variáveis de ambiente. Crie um arquivo '.env' na raiz do projeto contendo as credenciais do seu banco local (este arquivo é ignorado pelo Git):
   
   DB_NAME=agora
   DB_USER=postgres
   DB_PASSWORD=sua_senha_aqui
   DB_HOST=localhost
   DB_PORT=5432

--- COMO EXECUTAR ---

Sempre que a estrutura do banco mudar (novas tabelas, colunas ou chaves adicionadas), execute o extrator a partir da raiz do projeto:

   python catalog/extractor.py

Saída esperada: O arquivo 'catalog/data_catalog.json' será gerado ou sobrescrito automaticamente com a estrutura atualizada, pronto para ser consumido pelo módulo de LLM.

--- COMO TESTAR ---

Os testes automatizados validam a estrutura do JSON de saída e confirmam a presença das tabelas essenciais exigidas para a issue. Para executá-los:

   python -m unittest discover -s catalog/tests