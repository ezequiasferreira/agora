# Linguagem Natural e Geração de SQL do Ágora

Esta pasta concentra o módulo responsável por receber perguntas em linguagem natural, utilizar o catálogo de dados disponível e gerar consultas SQL compatíveis com a estrutura do banco.

O módulo também deve reconhecer perguntas que não podem ser respondidas com os dados disponíveis ou que precisam de esclarecimento antes da geração da consulta.

Responsável principal: Mateus.

# 🛠️ Pré-requisitos e Instalação

Para rodar este módulo, você precisará do Python instalado e das bibliotecas de comunicação e inteligência artificial. 

1. Abra o terminal na pasta `llm`.
2. Instale todas as dependências rodando o comando abaixo:
   ```bash
   pip install -r requirements.txt