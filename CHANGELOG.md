# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Diagramas de Venn (`figures/venn_*.png`, 300 dpi) e tabelas de
  sobreposição: hipertensão dentro das doenças cardíacas, diabetes
  dentro das metabólicas, HAS × DM, grupos de comorbidades,
  multimorbidade, tabagismo × etilismo (× SPAs). Guia
  `reports/comorbidades_habitos_venn.md` e seção "Venn" no HTML.
- Leitura das cores de preenchimento da planilha (verde/azul em
  doenças cardíacas, roxo/rosa em metabólicas) e colunas
  `outra_doenca_cardiaca` / `outra_doenca_metabolica`.
- `descriptive/qa_inconsistencias_cores.csv`: linhas em que a cor
  contradiz SIM/NÃO.
- Setup inicial do projeto via template ds-template-v2.
- Guia `reports/COMO_NAVEGAR.md` para a equipe de enfermagem.
- Gráficos interativos Plotly no relatório HTML (heatmap PhiK, barras
  de -log10(p) e barras por CSV descritivo).
- Figura estática `figures/association_pvalues.png` como alternativa
  offline ao gráfico interativo de p-valores.

### Fixed
- Valores ausentes (`pd.NA`) viravam o texto `"<NA>"` na padronização
  e contavam como categoria. Isso inflava os testes de associação
  (p ≈ 1e-70 em todas as variáveis); os resultados foram refeitos e
  doenças respiratórias deixam de ser significativas (p = 0,38).
- Figuras PNG agora são embutidas em base64 no HTML, que passa a
  exibir todos os gráficos após download ou envio por e-mail.

### Changed
- Base passa a ser a planilha revisada (out/2026); a versão anterior
  fica em `data/raw/..._versao_2026-08-13.xlsx`.
- Todo hipertenso conta em doenças cardíacas e todo diabético em
  doenças metabólicas (doenças cardíacas: 123 → 126).
- Seções do relatório padronizadas (`#associacao`, `#clinica`,
  `#figuras`, `#descritivos`), proporções exibidas em porcentagem e
  aviso quando os CSVs estão mais antigos que a base processada.