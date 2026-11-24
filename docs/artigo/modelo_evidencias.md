# Modelo de evidências para o artigo Ágora

Copie este modelo para cada caso de teste ou evidência técnica. Preencha somente com dados efetivamente observados.

## Identificação
- **Código**: EV-___
- **Responsável**:
- **Data e horário**:
- **Ambiente / versão / commit**:
- **Issue relacionada**:
- **Tipo**: teste funcional | revisão de código | histórico técnico | diagrama | documentação
- **Fonte original / caminho no repositório**:

## Caso de teste
- **Objetivo**:
- **Pergunta**:
- **Resultado esperado e fundamento**:
- **Estado da LLM exibido (se disponível)**:
- **SQL gerado (se disponível, sem valores sensíveis)**:
- **Resposta efetiva / agregados obtidos**:
- **Formato apresentado**: texto | tabela | gráfico
- **Tempo SQL registrado**:
- **Latência ponta a ponta (somente se medida)**:
- **Tokens registrados (se disponíveis)**:
- **Resultado**: aprovado | reprovado | inconclusivo | não executado
- **Evidência verificável**: link para arquivo, captura sanitizada, commit, log ou documentação
- **Limitações / observações**:

## Checagem de conformidade

- [ ] O dado veio de execução ou de fonte técnica identificável
- [ ] Data, ambiente e versão foram informados
- [ ] Não foram expostos dados pessoais ou segredos
- [ ] O SQL corresponde à pergunta e à unidade de contagem desejada
- [ ] Não foi afirmada média de desempenho com base em uma única medição
- [ ] Eventuais limitações e inconclusões foram registradas

## Matriz resumida sugerida

| ID | Pergunta/objetivo | Esperado | Obtido | SQL verificado? | Situação | Evidência |
|---|---|---|---|---|---|---|
| EV-01 | Contagem de janeiro/2025 | 1.338 conforme observação histórica do manuscrito | Pendente de reprodução | Pendente | Não executado | — |
| EV-02 | Agrupamento mensal em 2025 | Seis linhas jan–jun na observação histórica do manuscrito | Pendente de reprodução | Pendente | Não executado | — |
| EV-03 | Pergunta ambígua | Solicitação de esclarecimento segundo contrato técnico | Pendente de reprodução | Pendente | Não executado | — |
| EV-04 | Informação não disponível | Indicação de não respondível segundo contrato técnico | Pendente de reprodução | Pendente | Não executado | — |

**Importante:** os resultados históricos são referências para reproduzir; não significam que os testes novos foram realizados.
