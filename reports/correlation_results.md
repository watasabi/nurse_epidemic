# Correlações entre variáveis numéricas

Este relatório explica as correlações calculadas na Fase 2 (Pearson ou Spearman, com intervalo de confiança de 95%).

- Arquivo numérico: `reports/correlation_results.csv`
- Nível de significância: **5%**

## O que é correlação?

Correlação mede se duas variáveis numéricas **andam juntas**:

- **r próximo de +1**: quando uma sobe, a outra tende a subir.
- **r próximo de −1**: quando uma sobe, a outra tende a cair.
- **r próximo de 0**: pouco relacionamento linear/monotônico.

Correlação **não prova causa**; só descreve associação numérica.

## Pearson ou Spearman?

- **Pearson**: adequado quando as duas variáveis se aproximam de uma distribuição normal.
- **Spearman**: usa postos (ranks); preferido quando a normalidade falha (padrão clínico frequente).

O pipeline testa normalidade (Shapiro) e escolhe o método.

## Intervalo de confiança (IC 95%)

O IC 95% é uma faixa plausível para o verdadeiro r na população. Se o intervalo **cruza o zero**, a correlação costuma ser compatível com “sem associação”.

## Resultados

| Variável A | Variável B | Método | r | IC 95% | p-value | n |
|---|---|---|---|---|---|---|
| duracao_horas | faixa_etaria_ordinal | spearman | 0.0840 | [-0.026, 0.197] | 0.1294 | 327 |

## Interpretação prática

- `duracao_horas` × `faixa_etaria_ordinal`: correlação fraca (r ≈ 0.084), não significativa (p ≥ 0,05).

## Como usar

1. Use esta página para o texto de resultados/discussão.
2. Detalhes em `correlation_results.csv`.
3. Para associação categórica × desfecho, veja `association_results.md`.
