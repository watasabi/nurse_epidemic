# upa-analytics

## Status

`completed`

## Scope

Pipeline de análise epidemiológica UPA Curitiba (Fases 1 e 2):

- Pré-processamento e limpeza do Excel multi-aba
- Estatística descritiva (CSV + figuras)
- Testes de associação (χ²/Fisher, Mann-Whitney/Kruskal, PhiK)
- Correlações Pearson/Spearman com IC 95%
- Relatório HTML (classic + minimal)
- De-para de normalizações (colunas e valores) para leitura humana

## Claims

- [x] `prepare_data()` gera parquet com 328 registros
- [x] CSVs em `reports/descriptive/`, `association_results.csv`, `correlation_results.csv`
- [x] De-para exportado em `reports/depara_*.csv` e `docs/depara_normalizacoes.md`
- [x] HTML self-contained gerado
- [x] `uv run pytest tests/` passa

## References

- `docs/plano_implementacao_upa.md`
- `docs/plano_de_desenvolvimento.md`
