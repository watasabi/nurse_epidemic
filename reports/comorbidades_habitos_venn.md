# Comorbidades e hábitos de vida: sobreposições (Venn)

Um mesmo paciente pode ter mais de uma comorbidade ou hábito. Por isso as porcentagens de cada condição, somadas, passam de 100%. Os diagramas de Venn e as tabelas abaixo contam **cada paciente uma única vez**, na região que corresponde à sua combinação de condições.

- Tabelas: `descriptive/clin_cardiacas_hipertensao.csv`, `clin_metabolicas_diabetes.csv`, `clin_venn_*.csv` e `clin_multimorbidade.csv`
- Figuras (PNG 300 dpi, prontas para o trabalho): `figures/venn_*.png`
- Percentuais sobre os pacientes com informação (`n_valido`); na amostra atual todos os pacientes têm comorbidades e hábitos registrados.

## Como a planilha foi lida (marcação por cores)

| Coluna da planilha | Cor | Significado |
|---|---|---|
| DOENÇAS CARDÍACAS | verde | tem hipertensão (HAS) |
| DOENÇAS CARDÍACAS | azul | outra doença cardíaca, **sem** HAS |
| DOENÇAS METABÓLICAS | roxo | tem diabetes (DM) |
| DOENÇAS METABÓLICAS | rosa | outra doença metabólica, **sem** DM |

- Regra aplicada: todo hipertenso conta em doenças cardíacas e todo diabético em doenças metabólicas.
- **Limitação:** verde/roxo não exclui outra doença do mesmo grupo. Não dá para saber quantos hipertensos têm também outra doença cardíaca (idem para diabetes). Vale citar isso no texto.

## 1. Doenças cardíacas: hipertensão × outras

| Categoria | n | % |
|---|---:|---:|
| Doenças cardíacas (total) | 115 | 37,5% |
| Hipertensão arterial (HAS) | 108 | 35,2% |
| Outra doença cardíaca, sem HAS | 7 | 2,3% |
| Sem doenças cardíacas | 192 | 62,5% |

Das 115 pessoas com doenças cardíacas, 108 (93,9%) são hipertensas e 7 (6,1%) têm outra doença cardíaca, sem HAS.

Figura: `figures/venn_cardiacas_hipertensao.png` (esquema sem áreas proporcionais).

## 2. Doenças metabólicas: diabetes × outras

| Categoria | n | % |
|---|---:|---:|
| Doenças metabólicas (total) | 94 | 30,6% |
| Diabetes mellitus (DM) | 62 | 20,2% |
| Outra doença metabólica, sem DM | 32 | 10,4% |
| Sem doenças metabólicas | 213 | 69,4% |

Das 94 pessoas com doenças metabólicas, 62 (66,0%) são diabéticas e 32 (34,0%) têm outra doença metabólica, sem DM.

Figura: `figures/venn_metabolicas_diabetes.png` (esquema sem áreas proporcionais).

## 3. Hipertensão e diabetes

| Grupo | n | % |
|---|---:|---:|
| HAS + Diabetes | 47 | 15,3% |
| Somente HAS | 61 | 19,9% |
| Somente Diabetes | 15 | 4,9% |
| Nenhuma das condições | 184 | 59,9% |

Entre os hipertensos, 47 de 108 (43,5%) também são diabéticos; entre os diabéticos, 47 de 62 (75,8%) também são hipertensos.

Figura: `figures/venn_has_diabetes.png`.

## 4. Grupos de comorbidades

Doenças cardíacas (inclui HAS), metabólicas (inclui DM) e respiratórias crônicas.

| Combinação | n | % |
|---|---:|---:|
| Doenças cardíacas + Doenças metabólicas + Doenças respiratórias crônicas | 12 | 3,9% |
| Doenças cardíacas + Doenças metabólicas | 55 | 17,9% |
| Doenças cardíacas + Doenças respiratórias crônicas | 10 | 3,3% |
| Doenças metabólicas + Doenças respiratórias crônicas | 4 | 1,3% |
| Somente Doenças cardíacas | 38 | 12,4% |
| Somente Doenças metabólicas | 23 | 7,5% |
| Somente Doenças respiratórias crônicas | 21 | 6,8% |
| Nenhuma das condições | 144 | 46,9% |

Figura: `figures/venn_comorbidades.png`.

## 5. Multimorbidade

Quantos grupos de comorbidade cada paciente acumula (cardíacas, metabólicas, respiratórias crônicas, neoplasias e saúde mental).

| Nº de grupos | n | % |
|---|---:|---:|
| 0 | 96 | 31,3% |
| 1 | 111 | 36,2% |
| 2 | 79 | 25,7% |
| 3 | 17 | 5,5% |
| 4 | 4 | 1,3% |

100 de 307 (32,6%) pacientes têm dois ou mais grupos de comorbidade.

## 6. Hábitos de vida: tabagismo e etilismo

| Grupo | n | % |
|---|---:|---:|
| Tabagista + Etilista | 43 | 14,0% |
| Somente Tabagista | 57 | 18,6% |
| Somente Etilista | 20 | 6,5% |
| Nenhuma das condições | 187 | 60,9% |

Entre os tabagistas, 43 de 100 (43,0%) também são etilistas; entre os etilistas, 43 de 63 (68,3%) também são tabagistas.

Figura: `figures/venn_habitos.png`.

## 7. Tabagismo, etilismo e uso de SPAs

SPAs = substâncias psicoativas.

| Combinação | n | % |
|---|---:|---:|
| Tabagista + Etilista + Uso de SPAs | 28 | 9,1% |
| Tabagista + Etilista | 15 | 4,9% |
| Tabagista + Uso de SPAs | 4 | 1,3% |
| Etilista + Uso de SPAs | 2 | 0,7% |
| Somente Tabagista | 53 | 17,3% |
| Somente Etilista | 18 | 5,9% |
| Somente Uso de SPAs | 4 | 1,3% |
| Nenhuma das condições | 183 | 59,6% |

Figura: `figures/venn_habitos_spas.png`.

## Como ler um diagrama de Venn

- Cada círculo é uma condição; o número junto do nome é o total de pacientes com ela.
- Os números **dentro** das regiões são exclusivos: quem está na interseção não é contado de novo nas outras partes.
- Nos diagramas de 2 e 3 círculos, o tamanho é aproximadamente proporcional ao número de pacientes. Nos de hipertensão e diabetes dentro do grupo, o desenho é só esquemático.

## Pontos para revisar na planilha

Nenhuma inconsistência entre cores e SIM/NÃO.

## Regenerar

```bash
uv run python -m nurse_epidemic.pipeline.prepare_data
uv run python reports/export_clinical_summaries.py
uv run python reports/generate_profile_report.py
```
