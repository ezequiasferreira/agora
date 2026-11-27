# Parecer — verificação funcional e revisão do manuscrito v2 (ART-04)

**Autor:** Gustavo Inácio de Souza (UERR) · **Data:** 26/11/2026 · **Issue:** #15
**Materiais:** `matriz_testes_ART-04.md`, `revisao_artigo_achados.md`, `evidencias/`

## 1. Escopo

A verificação foi feita na aplicação publicada (https://agora.grupolealferreira.com.br/, API versão 0.3.0), em 24 e 25/11/2026, com o navegador Brave no Windows 11. Ela cobriu a interface (9 itens), as duas consultas da seção 6 do manuscrito, seis consultas adicionais, perguntas ambíguas, fora do domínio e de período sem dados, e quatro registros exploratórios. Em 26/11/2026 foram feitas a revisão do código (commit ca99ed5) e a revisão do manuscrito: formatação, referências, coerência com o código e com os testes, limitações e a leitura dos dois trabalhos citados. Todos os resultados são execuções isoladas, registradas uma a uma, e não constituem avaliação estatística.

## 2. Resultados da verificação funcional

- **Reproduções do manuscrito.** A consulta da seção 6.2 reproduziu os seis valores e o gráfico descritos (EV-02). A consulta da seção 6.1 retornou 1.338, com o SQL do manuscrito, em 9 de 10 execuções. Na outra execução, o resultado foi 9.484 (EV-01); esse valor coincide com a contagem de lançamentos de rubricas de janeiro/2025 (EV-12), mas o SQL dessa execução não foi capturado.
- **Interface.** Os 9 comportamentos descritos na seção 5 foram observados (EV-I01 a EV-I09).
- **Respostas sem consulta ao banco.** Perguntas ambíguas retornaram NEEDS_CLARIFICATION (EV-03), e uma pergunta fora do domínio retornou NOT_ANSWERABLE (EV-04), sem SQL, como prevê `docs/contratos.md`. A pergunta sobre um período fora da base retornou 0 (EV-05).
- **Variação entre execuções.** A mesma pergunta produziu SQL diferente em execuções distintas, com o mesmo resultado (EV-09) ou com resultados diferentes (EV-01; EX-02: erro e acerto com o mesmo texto).
- **Respostas com muitas linhas.** Quando a consulta retornou mais de 1.000 linhas, a resposta informou "1.000 registros" (EX-01, EX-03). No código, a leitura é limitada a 1.000 linhas e a contagem enviada à etapa de resposta é a das linhas lidas (RC-03).
- **Formato.** O atalho "Evolução mensal" respondeu em lista, sem tabela e sem gráfico, nas 2 execuções (EV-07). No gráfico de EV-02, os rótulos do eixo Y apareceram todos como "1,4": o gráfico leu "1.338" como 1,338 (A42).
- **Tempo.** Na única medição feita (EV-09), a latência total foi de 10,94 s, para um tempo de consulta exibido de 3 ms. Observação do testador, sem cronômetro: nas demais execuções, as respostas levaram tempo semelhante, em torno de 10 s. Essa percepção não é medição nem média.
- **Contagem de unidades.** "Quantas unidades existem?" retornou 344 valores distintos; a tabela tem 369 linhas (EV-10, EV-11). A resposta não informa o critério usado.

## 3. Revisão do manuscrito: síntese

Foram registrados 43 achados (`revisao_artigo_achados.md`), descritivos e acompanhados da norma ou do critério aplicável, além de 10 afirmações conferidas sem divergência (V01–V10), entre elas a soma das seis linhas da seção 6.2, que é igual ao total de registros informado no README (8.124). Os principais:

1. **Formatação (A01–A04, A32, A33).** As três tabelas não têm número, título nem fonte; os blocos de SQL não têm identificação; não há figuras; o Abstract não acompanha o Resumo e não traz Keywords; a linha de autoria está incompleta.
2. **Referências (A05–A15).** A fundamentação acadêmica se apoia em dois trabalhos. Quatro referências são documentos internos, sem citação no texto. Há "s.d." e citação em caixa alta, fora da NBR 10520:2023. As referências do Spider e do DIN-SQL estão incompletas.
3. **Trabalhos citados (A16, A17, A34–A37).** O resumo do Spider não sustenta que o conjunto "consolidou" a avaliação. A decomposição do DIN-SQL ocorre dentro da geração do SQL e é de natureza diferente da separação de responsabilidades do Ágora. Comportamentos observados nos testes correspondem à categoria de erro "schema linking" do DIN-SQL. O DIN-SQL informa custo e latência por pergunta.
4. **Coerência com o código (A19–A23, A38–A43).** O catálogo citado (5 tabelas, 74 colunas) não é o que está em uso (10 objetos, 178 colunas). Informações atribuídas ao "histórico" estão no repositório público. A biblioteca do gráfico (Chart.js) é identificável. A API publicada também expõe `POST /query`. O validador de SQL bloqueou os comandos de escrita testados (RC-01).
5. **Limitações (A24–A31).** O manuscrito não menciona a variação entre execuções, o efeito do limite de linhas na resposta, os status além de ANSWER, a versão testada nem o tratamento de dados pessoais.

## 4. Limitações desta verificação

- A latência total foi medida uma única vez.
- O SQL da execução com resultado 9.484 não foi capturado. A execução se sustenta no print, que mostra a pergunta no campo, e na redação da resposta, que repete os termos da pergunta ("Em janeiro de 2025, existem 9.484 registros de remuneração"). Quando a pergunta trata de rubricas, a resposta usa "lançamentos de rubricas da folha" (EV-12).
- Em várias execuções, o texto da pergunta não aparece na cópia, porque o campo é limpo após o envio. A origem de cada pergunta está indicada em `paineis_texto_bruto.md`.
- Não houve acesso direto ao banco. Os valores foram conferidos entre execuções e contra o manuscrito, não contra os dados originais.
- A identidade entre o código implantado e o commit ca99ed5 não foi verificada; só a versão declarada (0.3.0) coincide.
- O validador foi executado sobre o código, em ambiente isolado. As permissões do usuário do banco em produção não foram verificadas.
- As perguntas dos testes foram formuladas com apoio de ferramenta de IA, que também ajudou a organizar os registros. As execuções e as observações na aplicação foram feitas pelo autor.

## 5. Melhorias propostas

### Para o manuscrito
1. Numerar e intitular as tabelas e os quadros (seções 4 e 5 como quadros; 6.2 como tabela), com fonte, e identificar os blocos de SQL como listagens.
2. Incluir uma figura da arquitetura e uma captura da interface com o painel técnico, sem dados pessoais.
3. Completar a autoria (nomes, vínculo, contato), ajustar o Abstract ao Resumo e acrescentar Keywords.
4. Adequar citações e referências à NBR 10520:2023 e à NBR 6023, completar Spider (anais, local, páginas 3911–3921) e DIN-SQL (versão ou anais) e citar no texto as referências listadas, ou retirá-las.
5. Substituir "conforme histórico" pelo repositório público com commit (`api/app/main.py`, `frontend/`), sempre que a informação estiver no código.
6. Atualizar o número do catálogo (3.2) ou datá-lo; identificar a biblioteca do gráfico (4.1); atualizar a seção 4.2 com os controles confirmados no código (RC-01, RC-02) e com o que permanece sem comprovação.
7. Rever a frase sobre o Spider ("consolidou") e a relação entre o DIN-SQL e a separação de responsabilidades. Considerar o BIRD (citado pelo próprio DIN-SQL) para a fundamentação sobre bases reais.
8. Acrescentar uma subseção de dados: fonte, período (jan–jun/2025), volumes e tratamento de dados pessoais (LGPD).
9. Incorporar como limitações: a variação entre execuções, o efeito do limite de 1.000 linhas, os demais status (NEEDS_CLARIFICATION, NOT_ANSWERABLE, DB_QUERY_ERROR, FORMAT_ERROR) e a versão observada.
10. Relacionar os comportamentos observados à taxonomia de erros do DIN-SQL (schema linking) e situar tempo e custo em relação aos valores relatados na literatura citada.

### Para o software (trabalhos futuros)
1. **Indicar resultado limitado:** quando a consulta atingir `max_rows`, informar à etapa de resposta e ao usuário que o resultado foi cortado, ou contar o total separadamente.
2. **Autocorreção:** após `DB_QUERY_ERROR` ou `FORMAT_ERROR`, devolver o erro ao modelo para uma nova tentativa limitada, como o módulo de autocorreção do DIN-SQL.
3. **Informar o critério de contagem** na resposta (por exemplo, "344 nomes distintos de unidade") e o **período coberto** pela base quando a consulta retornar zero.
4. **Reduzir a variação:** fixar parâmetros de geração quando o provedor permitir, ou validar a tabela escolhida contra as regras do glossário antes de executar.
5. **Gráfico:** gerar o gráfico a partir do resultado estruturado da consulta, e não do texto da resposta. Hoje, números com ponto de milhar e sem vírgula, como "1.338", são lidos como decimais (1,338), e o eixo passa a mostrar "1,4" (A42).
6. **Custo:** configurar os preços por token no ambiente publicado, para que o custo estimado seja informativo.
7. **Cache:** avaliar cache de consultas para perguntas repetidas. A variante exata não usa a LLM; a variante semântica, por embeddings, exige checar datas e números para evitar falsos positivos, como "janeiro" × "fevereiro".
8. **Rastreabilidade:** exibir a versão ou o commit implantado no `/health` e permitir copiar a pergunta junto com o painel técnico.
9. **Endpoint `/query`:** avaliar se ele precisa ficar público (tema da issue #14).

### Para o processo de verificação
1. Repetir cada consulta de referência várias vezes e registrar todas as execuções.
2. Capturar sempre o SQL e cronometrar a latência total de cada consulta de referência.
3. Classificar as perguntas de teste pelos níveis de dificuldade do Spider (fácil, médio, difícil, extra difícil) e verificar, além do resultado, o SQL. O Spider aponta que a comparação só por resultado pode gerar falsos positivos.

## 6. Conclusão

O fluxo descrito no manuscrito foi reproduzido na aplicação publicada: as duas consultas da seção 6 retornaram os valores relatados, a interface apresentou os comportamentos descritos e o sistema recusou ou pediu esclarecimento nos casos previstos no contrato técnico. A verificação registrou também comportamentos não tratados no manuscrito, sobretudo a variação de resultados entre execuções da mesma pergunta e o efeito do limite de linhas nas respostas, que podem ser incorporados como limitações e trabalhos futuros. A revisão do texto aponta ajustes de formatação, de referências e de atualização em relação ao código, todos detalhados em `revisao_artigo_achados.md`.
