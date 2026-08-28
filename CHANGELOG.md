# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Setup inicial do projeto via template ds-template-v2.
- Guia `reports/COMO_NAVEGAR.md` para a equipe de enfermagem.
- Gráficos interativos Plotly no relatório HTML (heatmap PhiK, barras
  de -log10(p) e barras por CSV descritivo).
- Figura estática `figures/association_pvalues.png` como alternativa
  offline ao gráfico interativo de p-valores.

### Fixed
- Figuras PNG agora são embutidas em base64 no HTML, que passa a
  exibir todos os gráficos após download ou envio por e-mail.

### Changed
- Seções do relatório padronizadas (`#associacao`, `#clinica`,
  `#figuras`, `#descritivos`), proporções exibidas em porcentagem e
  aviso quando os CSVs estão mais antigos que a base processada.