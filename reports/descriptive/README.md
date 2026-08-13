# Relatórios descritivos (Fase 1)

Tabelas de frequência e resumos numéricos gerados a partir da base
limpa de atendimentos UPA (`upa_patients_clean.parquet`).

Amostra atual: **328** registros (abril + maio/2025).

## Como navegar

1. Comece pelos arquivos `demo_*` (perfil demográfico).
2. Em seguida, use os resumos agrupados `clin_desfecho`,
   `clin_setor_destinado`, `clin_comorbidades`, `clin_habitos_vida` e
   `clin_tempo_permanencia` — são os mais úteis para o texto do artigo.
3. Os demais `clin_*` detalham cada variável individualmente.

## Arquivos incluídos

### Demográficos (`demo_*`)

- `demo_sexo.csv` — distribuição por sexo (M/F)
- `demo_faixa_etaria.csv` — faixas 18–40, 40–60, 60–80, 80–100

### Resumos clínicos agrupados

- `clin_desfecho.csv` — desfecho padronizado (ALTA, INTERNAMENTO,
  ENCAMINHAMENTO, OBITO)
- `clin_desfecho_padronizado.csv` — mesma informação via relatório
  clínico genérico
- `clin_setor_destinado.csv` — eixo crítico, decisão, etc.
- `clin_tempo_permanencia.csv` — categorias ATE_6H … MAIS_24H
- `clin_comorbidades.csv` — prevalência (SIM) por tipo de comorbidade
- `clin_habitos_vida.csv` — tabagismo e etilismo

### Variáveis clínicas individuais (`clin_*`)

- `clin_comorbidade.csv` — presença geral de comorbidade (SIM/NAO)
- `clin_diabetico.csv`
- `clin_hipertenso.csv`
- `clin_saude_mental.csv`
- `clin_tabagista.csv`
- `clin_etilista.csv`
- `clin_uso_spas.csv`
- `clin_doencas_cardiacas.csv`
- `clin_doencas_respiratorias.csv`
- `clin_doencas_metabolicas.csv`
- `clin_neoplasias.csv`

### Numéricos

- `clin_idade_numerica.csv` — idade em anos (média, mediana, etc.)
- `clin_duracao_horas.csv` — duração do atendimento em horas
  (derivada de data/hora início e fim)

## Como interpretar

### Tabelas categóricas

Colunas típicas:

| Coluna | Significado |
|--------|-------------|
| `valor` | Categoria (ex.: SIM, ALTA, EIXO CRITICO) |
| `absoluta` | Número de pacientes nessa categoria |
| `relativa` | Proporção (0 a 1). Ex.: `0.25` = **25%** |

Em resumos como `clin_comorbidades.csv` / `clin_habitos_vida.csv`:

| Coluna | Significado |
|--------|-------------|
| `sim_absoluta` | Quantos responderam SIM |
| `sim_relativa` | Proporção de SIM entre válidos |
| `n_valido` | Quantos tinham informação preenchida |

### Tabelas numéricas

| Coluna | Significado |
|--------|-------------|
| `n` | Quantidade de valores válidos |
| `media` | Média aritmética |
| `mediana` | Valor central (menos sensível a extremos) |
| `min` / `max` | Extremos observados |
| `desvio_padrao` | Dispersão em torno da média |

## Dicas para a redação

- Sempre cite o **n** (ou `n_valido`) junto da porcentagem.
- Dados faltantes em comorbidades/hábitos são esperados em prontuário
  eletrônico; não invente valores — veja o de-para e a coluna `n`.
- Para cruzar essas tabelas com desfecho, use
  [`../association_results.md`](../association_results.md).

## Regenerar

```bash
uv run python reports/export_clinical_summaries.py
```
