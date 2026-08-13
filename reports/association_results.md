# Associação entre variáveis clínicas e desfecho

Este relatório explica, em linguagem simples, os testes usados para avaliar se características clínicas estão associadas ao desfecho do atendimento na UPA.

- Arquivo numérico: `reports/association_results.csv`
- Pacientes analisados (máx.): **328**
- Variável alvo: `desfecho_padronizado` (ALTA, INTERNAMENTO, ENCAMINHAMENTO, OBITO)
- Nível de significância: **5%** (p < 0.05)

## O que testamos?

Cada linha da tabela é uma variável clínica cruzada com o desfecho padronizado.

- Variáveis **categóricas** (SIM/NAO, setor, tempo): teste **χ²**; se a tabela for 2×2 com alguma célula < 5, usa-se **Fisher exato**.
- Variável **numérica** `duracao_horas`: **Kruskal-Wallis** (ou Mann-Whitney se houver só 2 grupos), comparando a distribuição da duração entre os desfechos.

### Por que esses testes?

- **χ² / Fisher**: a proporção de desfechos é diferente entre grupos? Ex.: tabagistas vs não tabagistas.
- **Kruskal-Wallis**: a duração do atendimento difere entre os grupos de desfecho, sem exigir normalidade dos dados.

## Como entender o valor-p

O p-valor é a probabilidade de vermos um resultado tão (ou mais) extremo **se não houvesse associação real**.

- Se p < 0.05: associação **estatisticamente significativa**.
- Se p ≥ 0.05: **não há evidência suficiente** de associação neste conjunto de dados.

### Hipótese nula

Para todos os testes: **não existe associação** entre a variável e o desfecho. Rejeitar a hipótese nula = há associação estatística (não implica, sozinha, causalidade clínica).

## Resultados principais

Variáveis com associação estatisticamente significativa:

- `comorbidade` — χ² (qui-quadrado): p ≈ 7.32e-69 (n = 328).
- `tabagista` — χ² (qui-quadrado): p ≈ 1.38e-68 (n = 328).
- `etilista` — χ² (qui-quadrado): p ≈ 1.33e-70 (n = 328).
- `doencas_cardiacas` — χ² (qui-quadrado): p ≈ 3.41e-71 (n = 328).
- `doencas_respiratorias` — χ² (qui-quadrado): p ≈ 9.88e-67 (n = 328).
- `doencas_metabolicas` — χ² (qui-quadrado): p ≈ 2.22e-69 (n = 328).
- `setor_destinado` — χ² (qui-quadrado): p ≈ 5.58e-39 (n = 328).
- `tempo_permanencia` — χ² (qui-quadrado): p ≈ 1.38e-68 (n = 328).

## Tabela completa dos testes

| Variável | Tipo de teste | p-value | n | Associação? |
|---|---|---|---|---|
| comorbidade | χ² (qui-quadrado) | 7.32e-69 | 328 | significativa |
| tabagista | χ² (qui-quadrado) | 1.38e-68 | 328 | significativa |
| etilista | χ² (qui-quadrado) | 1.33e-70 | 328 | significativa |
| doencas_cardiacas | χ² (qui-quadrado) | 3.41e-71 | 328 | significativa |
| doencas_respiratorias | χ² (qui-quadrado) | 9.88e-67 | 328 | significativa |
| doencas_metabolicas | χ² (qui-quadrado) | 2.22e-69 | 328 | significativa |
| setor_destinado | χ² (qui-quadrado) | 5.58e-39 | 328 | significativa |
| tempo_permanencia | χ² (qui-quadrado) | 1.38e-68 | 328 | significativa |
| duracao_horas | Kruskal-Wallis | 0.6501 | 327 | não significativa |

## Matriz PhiK

Além dos p-valores, geramos uma matriz PhiK (`association_phik_matrix.csv` e figura `figures/association_phik_matrix.png`).

- Escala de **0 a 1** (quanto maior, mais associação).
- Útil como visão geral entre várias variáveis ao mesmo tempo.

## Como usar este relatório

1. Leia os resultados principais acima.
2. Confira números em `association_results.csv`.
3. Compare com os gráficos em `figures/` e as tabelas em `descriptive/`.
4. Para saber como os valores brutos foram padronizados, veja `../docs/depara_normalizacoes.md`.

## Gerar o HTML interativo

```bash
uv run python reports/generate_profile_report.py
```

Isso atualiza `profile_report.html` e `profile_report_minimal.html`.
