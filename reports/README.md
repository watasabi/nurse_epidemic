# Relatórios — Perfil Epidemiológico UPA Curitiba

Esta pasta concentra os **entregáveis legíveis** da análise: tabelas,
figuras, testes estatísticos e relatórios HTML.

O público-alvo inclui a equipe clínica e quem for redigir o artigo —
não é necessário saber programar para navegar pelos arquivos.

## Por onde começar?

| Ordem | Arquivo / pasta | O que você encontra |
|------:|-----------------|---------------------|
| 1 | [`profile_report_minimal.html`](profile_report_minimal.html) | Visão completa em HTML (recomendada) |
| 2 | [`descriptive/README.md`](descriptive/README.md) | Como ler as tabelas descritivas |
| 3 | [`figures/README.md`](figures/README.md) | Lista e sentido de cada gráfico |
| 4 | [`association_results.md`](association_results.md) | Como interpretar χ² / Kruskal / p-valor |
| 5 | [`correlation_results.md`](correlation_results.md) | Como interpretar Pearson / Spearman e IC 95% |
| 6 | [`../docs/depara_normalizacoes.md`](../docs/depara_normalizacoes.md) | De-para original → padronizado |

## Mapa dos arquivos

### Descritiva (Fase 1)

- Pasta [`descriptive/`](descriptive/) — CSVs `demo_*` (demografia) e
  `clin_*` (clínica)
- Prefixo `demo_`: perfil socioeconômico básico (sexo, faixa etária)
- Prefixo `clin_`: comorbidades, hábitos, setor, tempo, desfecho etc.

### Figuras

- Pasta [`figures/`](figures/) — PNGs para o artigo e o HTML

### Inferência (Fase 2)

- [`association_results.csv`](association_results.csv) — tabela numérica
  dos testes vs `desfecho_padronizado`
- [`association_results.md`](association_results.md) — interpretação em
  português
- [`association_phik_matrix.csv`](association_phik_matrix.csv) — matriz
  PhiK (0–1) entre variáveis mistas
- [`correlation_results.csv`](correlation_results.csv) — correlações
  numéricas
- [`correlation_results.md`](correlation_results.md) — interpretação

### De-para (rastreabilidade)

- [`depara_colunas.csv`](depara_colunas.csv) — nome Excel → snake_case
- [`depara_valores.csv`](depara_valores.csv) — valor bruto → normalizado
- [`depara_regras.csv`](depara_regras.csv) — regras documentadas

### Relatórios HTML

- [`profile_report.html`](profile_report.html) — tema clássico
- [`profile_report_minimal.html`](profile_report_minimal.html) — tema
  minimal (melhor para leitura)

## Como regenerar tudo

Na raiz do projeto:

```bash
uv run python -m nurse_epidemic.pipeline.prepare_data
uv run python reports/export_clinical_summaries.py
uv run python reports/generate_profile_report.py
```

## Glossário rápido

| Termo | Significado simples |
|-------|---------------------|
| `absoluta` | Quantidade de pacientes (n) |
| `relativa` | Proporção (0–1); multiplique por 100 para %) |
| p-valor | Chance do resultado se **não** houvesse associação real |
| significativo | p < 0,05 (convenção deste estudo) |
| PhiK | Medida de associação 0–1 para variáveis mistas |
| `desfecho_padronizado` | Alta / Internamento / Encaminhamento / Óbito |
