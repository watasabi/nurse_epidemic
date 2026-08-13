# De-para de normalizações — UPA Curitiba

Este documento descreve como os dados originais da planilha foram renomeados e padronizados. Os CSVs espelham estas tabelas em `reports/depara_*.csv`.

## 1. Colunas (Excel → snake_case)

| coluna_original_excel | coluna_normalizada | tipo_mapeamento | observacao |
| --- | --- | --- | --- |
| DATA DO INÍCIO DA CONSULTA | data_inicio_consulta | principal |  |
| INICIO DA CONSULTA | hora_inicio_consulta | principal |  |
| INÍCIO DA CONSULTA | hora_inicio_consulta | alias |  |
| DATA DO FINAL DA CONSULTA | data_fim_consulta | principal |  |
| FINAL DA CONSULTA | hora_fim_consulta | principal |  |
| DATA DE NASCIMENTO | data_nascimento | principal |  |
| IDADE | faixa_etaria | principal |  |
| IDADE.1 | idade_numerica | principal |  |
| SEXO (F / M) | sexo | principal |  |
| CID Admissão | cid_admissao | principal |  |
| FLUXOGRAMA UTILIZADO NA CR | fluxograma | principal |  |
| DESCRIMINADOR | discriminador | principal |  |
| PRIORIDADE | prioridade | principal |  |
| Desc. CID Admissão | desc_cid_admissao | principal |  |
| SETOR DESTINADO | setor_destinado | principal |  |
| Data Diagnóstico Admissão | data_diag_admissao | principal |  |
| Desc. CID Alta | desc_cid_alta | principal |  |
| Data Diagnóstico Alta | data_diag_alta | principal |  |
| COMORBIDADE  (SIM OU NÃO) | comorbidade | principal |  |
| COMORBIDADES (SIM OU NÃO) | comorbidade | alias |  |
| Diabético | diabetico | principal |  |
| Hipertenso | hipertenso | principal |  |
| Saúde mental | saude_mental | principal |  |
| TABAGISTA | tabagista | principal |  |
| ETILISTA | etilista | principal |  |
| USO DE SPAS | uso_spas | principal |  |
| DOENÇAS CARDÍACAS | doencas_cardiacas | principal |  |
| DOENÇAS RESPIRATÓRIAS CRÔNICAS | doencas_respiratorias | principal |  |
| NEOPLASIAS | neoplasias | principal |  |
| DOENÇAS METABÓLICAS | doencas_metabolicas | principal |  |
| TEMPO TOTAL DE PERMANÊNCIA NA UPA | tempo_permanencia | principal |  |
| DESFECHO FINAL | desfecho | principal |  |
| INÍCIO DA CONSULTA | hora_inicio_consulta | alias_aba | Unificado com 'INICIO DA CONSULTA' |
| COMORBIDADES (SIM OU NÃO) | comorbidade | alias_aba | Unificado com 'COMORBIDADE  (SIM OU NÃO)' |
| (derivada) | duracao_horas | derivada | Calculada: data/hora fim − data/hora início |
| (derivada) | desfecho_padronizado | derivada | Agrupamento de DESFECHO FINAL |

## 2. Regras de normalização de valores

| grupo_regra | padrao_original | valor_normalizado |
| --- | --- | --- |
| sexo | M / MASCULINO | M |
| sexo | F / FEMININO | F |
| sexo | Outros | OUTRO |
| sim_nao | SIM / S / SIM_* | SIM |
| sim_nao | NÃO / NAO / N / NEGA | NAO |
| desfecho_padronizado | ALTA* | ALTA |
| desfecho_padronizado | TRANSFERENCIA* / TRANSFERÊNCIA* | INTERNAMENTO |
| desfecho_padronizado | CAPS / EVASAO / ENCERRAMENTO* | ENCAMINHAMENTO |
| desfecho_padronizado | OBITO* / ÓBITO* | OBITO |
| tempo_permanencia | ATÉ 6H (variantes com espaço) | ATE_6H |
| tempo_permanencia | ATÉ 12H | ATE_12H |
| tempo_permanencia | ATÉ 24H | ATE_24H |
| tempo_permanencia | MAIS DE 24H | MAIS_24H |
| setor_destinado | Texto normalizado (maiúsculas, sem acentos) | valor literal |

## 3. Valores observados (original → normalizado)

### `sexo`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| sexo | F | F | 150 |
| sexo | M | M | 178 |

### `faixa_etaria`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| faixa_etaria | 18-40 | 18-40 | 116 |
| faixa_etaria | 40-60 | 40-60 | 85 |
| faixa_etaria | 60-80 | 60-80 | 80 |
| faixa_etaria | 80-100 | 80-100 | 47 |

### `comorbidade`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| comorbidade | NÃO | NAO | 127 |
| comorbidade | SIM | SIM | 200 |
| comorbidade | <NA> | <NA> | 1 |

### `diabetico`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| diabetico | NÃO | NAO | 259 |
| diabetico | SIM | SIM | 69 |

### `hipertenso`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| hipertenso | NÃO | NAO | 211 |
| hipertenso | SIM | SIM | 117 |

### `saude_mental`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| saude_mental | NÃO | NAO | 248 |
| saude_mental | SIM | SIM | 80 |

### `tabagista`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| tabagista | NÃO | NAO | 221 |
| tabagista | SIM | SIM | 106 |
| tabagista | <NA> | <NA> | 1 |

### `etilista`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| etilista | NÃO | NAO | 261 |
| etilista | SIM | SIM | 66 |
| etilista | <NA> | <NA> | 1 |

### `uso_spas`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| uso_spas | NÃO | NAO | 287 |
| uso_spas | NÃO  | NAO | 1 |
| uso_spas | SIM | SIM | 39 |
| uso_spas | <NA> | <NA> | 1 |

### `doencas_cardiacas`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| doencas_cardiacas | NAO | NAO | 1 |
| doencas_cardiacas | NÃO | NAO | 203 |
| doencas_cardiacas | SIM | SIM | 123 |
| doencas_cardiacas | <NA> | <NA> | 1 |

### `doencas_respiratorias`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| doencas_respiratorias | NÃO | NAO | 276 |
| doencas_respiratorias | SIM | SIM | 51 |
| doencas_respiratorias | <NA> | <NA> | 1 |

### `neoplasias`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| neoplasias | NÃO | NAO | 321 |
| neoplasias | SIM | SIM | 6 |
| neoplasias | <NA> | <NA> | 1 |

### `doencas_metabolicas`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| doencas_metabolicas | NÃO | NAO | 222 |
| doencas_metabolicas | NÃO  | NAO | 1 |
| doencas_metabolicas | SIM | SIM | 104 |
| doencas_metabolicas | <NA> | <NA> | 1 |

### `setor_destinado`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| setor_destinado | EIXO CRÍTICO | EIXO CRITICO | 171 |
| setor_destinado | EIXO DECISÃO | EIXO DECISAO | 127 |
| setor_destinado | EIXO ISOLAMENTO | EIXO ISOLAMENTO | 1 |
| setor_destinado | SUTURA | SUTURA | 2 |
| setor_destinado | <NA> | <NA> | 27 |

### `tempo_permanencia`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| tempo_permanencia | ATÉ 12H | ATE_12H | 48 |
| tempo_permanencia | ATÉ 12H  | ATE_12H | 3 |
| tempo_permanencia | ATÉ 24H | ATE_24H | 60 |
| tempo_permanencia | ATÉ 24H  | ATE_24H | 9 |
| tempo_permanencia | ATÉ 6H | ATE_6H | 116 |
| tempo_permanencia | ATÉ 6H  | ATE_6H | 4 |
| tempo_permanencia | MAIS DE 24H | MAIS_24H | 37 |
| tempo_permanencia | MAIS DE 24H  | MAIS_24H | 50 |
| tempo_permanencia | <NA> | <NA> | 1 |

### `desfecho`

| coluna_normalizada | valor_original | valor_normalizado | n |
| --- | --- | --- | --- |
| desfecho | ALTA- ÓBITO RECENTE. | ALTA- OBITO RECENTE | 3 |
| desfecho | ALTA. | ALTA | 145 |
| desfecho | CAPS. | CAPS | 23 |
| desfecho | ENCERRAMENTO ADMINISTRATIVO. | ENCERRAMENTO ADMINISTRATIVO | 2 |
| desfecho | EVASÃO. | EVASAO | 23 |
| desfecho | TRANSFERÊNCIA HOSPITALAR – ÓBITO RECENTE. | TRANSFERENCIA HOSPITALAR – OBITO RECENTE | 3 |
| desfecho | TRANSFERÊNCIA HOSPITALAR- ÓBITO RECENTE. | TRANSFERENCIA HOSPITALAR- OBITO RECENTE | 9 |
| desfecho | TRANSFERÊNCIA HOSPITALAR-ÓBITO RECENTE. | TRANSFERENCIA HOSPITALAR-OBITO RECENTE | 1 |
| desfecho | TRANSFERÊNCIA HOSPITALAR. | TRANSFERENCIA HOSPITALAR | 116 |
| desfecho | TRANSFERÊNCIA HOSPÍTALAR. | TRANSFERENCIA HOSPITALAR | 1 |
| desfecho | ÓBITO. | OBITO | 1 |
| desfecho | <NA> | <NA> | 1 |
