# Figuras (gráficos)

Gráficos gerados automaticamente a partir da base processada do
estudo (UPA única, período abril–maio/2025).

Formato: PNG, resolução ≥ 120 dpi — adequados para inserção no artigo
ou apresentação.

## Gráficos disponíveis

| Arquivo | O que mostra | Uso sugerido |
|---------|--------------|--------------|
| `sexo_bar.png` | Contagem por sexo | Perfil demográfico |
| `desfecho_bar.png` | Desfecho padronizado | Resultado principal do estudo |
| `setor_bar.png` | Setor destinado na UPA | Fluxo assistencial |
| `fluxograma_bar.png` | Top 15 fluxogramas de classificação de risco | Perfil de queixas na triagem |
| `discriminador_bar.png` | Top 15 discriminadores de classificação de risco | Critérios de prioridade na triagem |
| `association_phik_matrix.png` | Mapa de calor PhiK (0–1) | Visão geral de associações |
| `association_pvalues.png` | -log10(p) por variável testada | Ranking de evidência estatística |

## Como interpretar

- Barras horizontais: categorias no eixo vertical; tamanho da barra =
  quantidade absoluta de pacientes.
- `fluxograma_bar.png` e `discriminador_bar.png` mostram só as 15
  categorias mais frequentes (a lista completa, com todas as
  categorias, está em `../descriptive/clin_fluxograma.csv` e
  `../descriptive/clin_discriminador.csv`).
- Matriz PhiK: valores próximos de **1** indicam associação forte
  entre o par de variáveis; próximos de **0**, associação fraca.
  Complementa (não substitui) os p-valores de
  [`../association_results.md`](../association_results.md).
- `association_pvalues.png`: barra maior = evidência mais forte. A
  linha tracejada vermelha marca p = 0,05; barras azuis ultrapassam
  esse limite (associação significativa), cinzas não.

## Como usar

1. Abra a figura no visualizador de imagens ou pelo HTML
   (`../profile_report_minimal.html`).
2. Escolha o gráfico que ilustra o parágrafo do artigo.
3. Na legenda do artigo, cite a fonte: dados da UPA Curitiba
   (Manchester / muito urgente), período abril–maio/2025.

## Regenerar

```bash
uv run python reports/export_clinical_summaries.py
```
