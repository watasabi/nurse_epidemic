# Figuras (gráficos)

Gráficos gerados automaticamente a partir da base processada e do
arquivo auxiliar `data/external/doencas_upa.csv`.

Formato: PNG, resolução ≥ 120 dpi — adequados para inserção no artigo
ou apresentação.

## Gráficos disponíveis

| Arquivo | O que mostra | Uso sugerido |
|---------|--------------|--------------|
| `sexo_bar.png` | Contagem por sexo | Perfil demográfico |
| `desfecho_bar.png` | Desfecho padronizado | Resultado principal do estudo |
| `setor_bar.png` | Setor destinado na UPA | Fluxo assistencial |
| `doencas_upa_trend.png` | Contagens por grupo de doença × mês/UPA | Contexto epidemiológico externo |
| `association_phik_matrix.png` | Mapa de calor PhiK (0–1) | Visão geral de associações |

## Como interpretar

- Barras horizontais: categorias no eixo vertical; tamanho da barra =
  quantidade absoluta de pacientes.
- `doencas_upa_trend.png`: cada grupo de doença tem várias barras
  (período × UPA). Serve para contextualizar o volume por tipo de
  agravo, **não** é o mesmo N da amostra de 328 prontuários.
- Matriz PhiK: valores próximos de **1** indicam associação forte
  entre o par de variáveis; próximos de **0**, associação fraca.
  Complementa (não substitui) os p-valores de
  [`../association_results.md`](../association_results.md).

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
