# Comorbidades e hábitos de vida: sobreposições (Venn)

Um mesmo paciente pode ter mais de uma comorbidade ou hábito. Por isso as porcentagens de cada condição, somadas, passam de 100%. Os diagramas de Venn e as tabelas abaixo contam **cada paciente uma única vez**, na região que corresponde à sua combinação de condições.

- Tabelas: `descriptive/clin_cardiacas_hipertensao.csv`, `clin_metabolicas_diabetes.csv`, `clin_venn_*.csv` e `clin_multimorbidade.csv`
- Figuras (PNG 300 dpi, prontas para o trabalho): `figures/venn_*.png`
- Percentuais sobre os pacientes com informação (`n_valido`). Um paciente sem registro de comorbidades/hábitos fica fora das análises que usam essas colunas; por isso alguns n são 327 e outros 328.

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
| Doenças cardíacas (total) | 126 | 38,5% |
| Hipertensão arterial (HAS) | 117 | 35,8% |
| Outra doença cardíaca, sem HAS | 9 | 2,8% |
| Sem doenças cardíacas | 201 | 61,5% |

Das 126 pessoas com doenças cardíacas, 117 (92,9%) são hipertensas e 9 (7,1%) têm outra doença cardíaca, sem HAS.

Figura: `figures/venn_cardiacas_hipertensao.png` (esquema sem áreas proporcionais).

## 2. Doenças metabólicas: diabetes × outras

| Categoria | n | % |
|---|---:|---:|
| Doenças metabólicas (total) | 104 | 31,8% |
| Diabetes mellitus (DM) | 69 | 21,1% |
| Outra doença metabólica, sem DM | 35 | 10,7% |
| Sem doenças metabólicas | 223 | 68,2% |

Das 104 pessoas com doenças metabólicas, 69 (66,3%) são diabéticas e 35 (33,7%) têm outra doença metabólica, sem DM.

Figura: `figures/venn_metabolicas_diabetes.png` (esquema sem áreas proporcionais).

## 3. Hipertensão e diabetes

| Grupo | n | % |
|---|---:|---:|
| HAS + Diabetes | 51 | 15,5% |
| Somente HAS | 66 | 20,1% |
| Somente Diabetes | 18 | 5,5% |
| Nenhuma das condições | 193 | 58,8% |

Entre os hipertensos, 51 de 117 (43,6%) também são diabéticos; entre os diabéticos, 51 de 69 (73,9%) também são hipertensos.

Figura: `figures/venn_has_diabetes.png`.

## 4. Grupos de comorbidades

Doenças cardíacas (inclui HAS), metabólicas (inclui DM) e respiratórias crônicas.

| Combinação | n | % |
|---|---:|---:|
| Doenças cardíacas + Doenças metabólicas + Doenças respiratórias crônicas | 14 | 4,3% |
| Doenças cardíacas + Doenças metabólicas | 60 | 18,3% |
| Doenças cardíacas + Doenças respiratórias crônicas | 11 | 3,4% |
| Doenças metabólicas + Doenças respiratórias crônicas | 4 | 1,2% |
| Somente Doenças cardíacas | 41 | 12,5% |
| Somente Doenças metabólicas | 26 | 8,0% |
| Somente Doenças respiratórias crônicas | 22 | 6,7% |
| Nenhuma das condições | 149 | 45,6% |

Figura: `figures/venn_comorbidades.png`.

## 5. Multimorbidade

Quantos grupos de comorbidade cada paciente acumula (cardíacas, metabólicas, respiratórias crônicas, neoplasias e saúde mental).

| Nº de grupos | n | % |
|---|---:|---:|
| 0 | 100 | 30,6% |
| 1 | 117 | 35,8% |
| 2 | 84 | 25,7% |
| 3 | 22 | 6,7% |
| 4 | 4 | 1,2% |

110 de 327 (33,6%) pacientes têm dois ou mais grupos de comorbidade.

## 6. Hábitos de vida: tabagismo e etilismo

| Grupo | n | % |
|---|---:|---:|
| Tabagista + Etilista | 46 | 14,1% |
| Somente Tabagista | 60 | 18,3% |
| Somente Etilista | 20 | 6,1% |
| Nenhuma das condições | 201 | 61,5% |

Entre os tabagistas, 46 de 106 (43,4%) também são etilistas; entre os etilistas, 46 de 66 (69,7%) também são tabagistas.

Figura: `figures/venn_habitos.png`.

## 7. Tabagismo, etilismo e uso de SPAs

SPAs = substâncias psicoativas.

| Combinação | n | % |
|---|---:|---:|
| Tabagista + Etilista + Uso de SPAs | 28 | 8,6% |
| Tabagista + Etilista | 18 | 5,5% |
| Tabagista + Uso de SPAs | 5 | 1,5% |
| Etilista + Uso de SPAs | 2 | 0,6% |
| Somente Tabagista | 55 | 16,8% |
| Somente Etilista | 18 | 5,5% |
| Somente Uso de SPAs | 4 | 1,2% |
| Nenhuma das condições | 197 | 60,2% |

Figura: `figures/venn_habitos_spas.png`.

## Como ler um diagrama de Venn

- Cada círculo é uma condição; o número junto do nome é o total de pacientes com ela.
- Os números **dentro** das regiões são exclusivos: quem está na interseção não é contado de novo nas outras partes.
- Nos diagramas de 2 e 3 círculos, o tamanho é aproximadamente proporcional ao número de pacientes. Nos de hipertensão e diabetes dentro do grupo, o desenho é só esquemático.

## Pontos para revisar na planilha

Linhas em que a cor contradiz as colunas SIM/NÃO (lista completa em `descriptive/qa_inconsistencias_cores.csv`):

- Aba MAIO_2025, linha 44: hipertenso = SIM, mas doencas_cardiacas não é SIM.
- Aba MAIO_2025, linha 46: doencas_cardiacas com a cor de hipertenso, mas hipertenso não é SIM.

Enquanto não forem corrigidas, vale a regra acima: hipertensão vem da coluna *Hipertenso* e 'outra cardíaca' vem da célula azul (idem para diabetes/rosa).

## Regenerar

```bash
uv run python -m nurse_epidemic.pipeline.prepare_data
uv run python reports/export_clinical_summaries.py
uv run python reports/generate_profile_report.py
```
