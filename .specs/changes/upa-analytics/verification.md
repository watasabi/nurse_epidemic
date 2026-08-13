# Verification: upa-analytics

- [x] `uv sync`
- [x] `uv run ruff check src/ tests/ reports/`
- [x] `uv run ruff format src/ tests/ reports/`
- [x] `uv run pytest tests/`
- [x] `uv run python reports/export_clinical_summaries.py`
- [x] `uv run python reports/generate_profile_report.py`
- [x] Parquet: 328 linhas em `data/processed/upa_patients_clean.parquet`
- [x] De-para: `reports/depara_colunas.csv`, `reports/depara_valores.csv`
- [x] Doc: `docs/depara_normalizacoes.md` atualizado
