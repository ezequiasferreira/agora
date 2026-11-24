# Artigo acadêmico — Ágora

## Escopo editorial
**Título de trabalho:** Ágora: desenvolvimento de uma aplicação web para consulta a dados institucionais com Text-to-SQL e modelos de linguagem.

**Natureza:** relato técnico-científico de **engenharia e desenvolvimento do software**. Priorizar arquitetura, decisões de implementação, tecnologias, integração, fluxo Text-to-SQL, funcionalidades e evidências verificáveis. Não confundir os testes funcionais da versão 2 com avaliação estatística de acurácia ou verificação exaustiva de segurança.

**Fonte editorial inicial:** `Artigo_Agora_Desenvolvimento_Software_v2.docx` (documento de trabalho fornecido à equipe, ainda não incorporado ao repositório).
**Aplicação:** https://agora.grupolealferreira.com.br/
**Repositório:** https://github.com/ezequiasferreira/agora

## Gestão das entregas

| Código | Issue | Responsável | Entrega | Prazo proposto |
|---|---|---|---|---|
| ART-01 | [#12](../../issues/12) | Ezequias | Redação, coordenação e consolidação | 02/12; revisão final 04/12/2026 |
| ART-02 | [#13](../../issues/13) | Matheus (@MatheusVSA) | IA e Text-to-SQL | 27/11/2026 |
| ART-03 | [#14](../../issues/14) | Gelson (@gelson35) | Backend, arquitetura e segurança | 27/11/2026 |
| ART-04 | [#15](../../issues/15) | Gustavo Inácio de Souza | Testes, evidências e revisão | plano 27/11; entrega 02/12/2026 |

**Atribuição pendente:** login GitHub de Gustavo. Não pressupor identidade baseada apenas no nome.

## Fluxo de trabalho

1. O responsável produz sua contribuição no arquivo de trabalho apropriado, incluindo fonte, data e versão.
2. Acrescenta links para commits, código, documentação, saídas de teste ou imagens **sem dados pessoais ou credenciais** na respectiva Issue.
3. Registra o que foi verificado, o que é somente documentação histórica e o que permanece sem comprovação.
4. Marca as caixas da Issue conforme as evidências ficarem disponíveis.
5. Solicita revisão cruzada. A equipe revisa antes de marcar como concluído.
6. Ezequias integra a contribuição ao manuscrito e registra a versão final.

### Estados sugeridos

- **A fazer**: nenhuma evidência registrada.
- **Em andamento**: trabalho iniciado.
- **Em revisão**: entregável anexado, aguardando conferência.
- **Concluído**: material conferido e incorporado ao artigo.

## Regra de qualidade e segurança

- Não publicar credenciais, URLs privadas, chaves, dados pessoais identificáveis ou conteúdo institucional sigiloso.
- Não declarar resultados ou testes inexistentes.
- Preservar a diferença entre **tempo SQL** e **latência total** da requisição.
- Distinguir o código da versão em produção, as decisões registradas no histórico e a intenção arquitetural.
- Conferir referências bibliográficas e contribuições autorais antes da submissão.

## Estrutura de apoio

- [Modelo de evidências](modelo_evidencias.md)
- [Acompanhamento editorial](acompanhamento.md)

## Relação com o desenvolvimento anterior

As Issues #1, #2, #3, #4, #5, #7 e #10 continuam como registros técnicos do desenvolvimento. As Issues #12–#15 tratam **exclusivamente da elaboração científica**, sem substituir, alterar ou encerrar atividades de software.
