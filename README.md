<a name="readme-top"></a>

<div align="center">
  <h1 align="center">nurse_epidemic</h1>
  <p align="center">
    Análise epidemiológica de pacientes classificados como muito urgentes
    (Protocolo de Manchester) em UPA de Curitiba-PR.
    <br />
    <br />
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Status-Development-yellow?style=for-the-badge" alt="Status">
  </p>
</div>

<details>
  <summary>Tabela de Conteúdos</summary>
  <ol>
    <li><a href="#sobre-o-projeto">Sobre o Projeto</a></li>
    <li><a href="#inicio-rapido">Início Rápido</a></li>
    <li><a href="#pipeline-de-analise">Pipeline de Análise</a></li>
    <li><a href="#de-para-de-normalizacoes">De-para de Normalizações</a></li>
    <li><a href="#organizacao-e-estrutura">Organização e Estrutura</a></li>
    <li><a href="#documentacao">Documentação</a></li>
    <li><a href="#convencao-de-commits">Convenção de Commits</a></li>
    <li><a href="#autor">Autor</a></li>
  </ol>
</details>

---

## Sobre o Projeto

Pacote Python para o estudo **Perfil epidemiológico e desfechos clínicos de
pacientes classificados como muito urgentes pelo Protocolo de Manchester em
uma Unidade de Pronto Atendimento em Curitiba-PR**.

O pipeline cobre:

1. **Pré-processamento** — leitura do Excel multi-aba, harmonização de
   colunas e padronização de valores
2. **Estatística descritiva** — frequências absolutas/relativas e medidas
   de tendência/dispersão
3. **Inferência** — χ²/Fisher, Mann-Whitney/Kruskal-Wallis, PhiK
4. **Correlações** — Pearson/Spearman com IC 95%
5. **Relatórios** — CSVs, figuras PNG e HTML (classic + minimal)

Amostra processada atual: **328 atendimentos** (abas `ABRIL_2025` +
`MAIO_2025`).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Início Rápido

```bash
# Ambiente
uv sync

# Preparar dados (Excel → parquet + de-para)
uv run python -m nurse_epidemic.pipeline.prepare_data

# Exportar descritivas, associações, correlações e figuras
uv run python reports/export_clinical_summaries.py

# Gerar relatórios HTML
uv run python reports/generate_profile_report.py

# Qualidade
uv run ruff check src/ tests/ reports/
uv run pytest tests/
```

Pré-requisito de dados: colocar a planilha em

`data/raw/Planilha de dados- Estátistico.xlsx`

(os diretórios `data/*` estão no `.gitignore`; apenas artefatos em
`reports/` e a documentação em `docs/` entram no repositório).

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Pipeline de Análise

```text
Excel multi-aba
  → io/loaders.py
  → cleaning/standardize.py (+ depara)
  → data/processed/upa_patients_clean.parquet
  → stats/descriptive | association | correlation
  → reports/*.csv, figures/*.png
  → profile_report.html (+ minimal)
```

| Saída | Caminho |
|-------|---------|
| Parquet limpo | `data/processed/upa_patients_clean.parquet` |
| Descritivas | `reports/descriptive/` |
| Associações | `reports/association_results.csv` / `.md` |
| PhiK | `reports/association_phik_matrix.csv` |
| Correlações | `reports/correlation_results.csv` |
| HTML | `reports/profile_report.html` |
| HTML minimal | `reports/profile_report_minimal.html` |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## De-para de Normalizações

Para leitura humana (pesquisadora e revisão posterior), o projeto gera um
mapa explícito entre dados originais e valores padronizados:

| Artefato | Conteúdo |
|----------|----------|
| [`docs/depara_normalizacoes.md`](docs/depara_normalizacoes.md) | Documentação legível |
| `reports/depara_colunas.csv` | Excel → snake_case |
| `reports/depara_valores.csv` | Valor original → normalizado (+ n) |
| `reports/depara_regras.csv` | Regras documentadas |

O de-para é regenerado automaticamente em cada execução de
`prepare_data()`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Organização e Estrutura

```text
.
├── docs/
│   ├── plano_de_desenvolvimento.md   # Escopo contratual (Fases 1–2)
│   ├── plano_implementacao_upa.md    # Plano técnico de implementação
│   └── depara_normalizacoes.md       # De-para legível
├── reports/
│   ├── export_clinical_summaries.py
│   ├── generate_profile_report.py
│   ├── descriptive/                  # CSVs demo_* / clin_*
│   ├── figures/                      # PNGs
│   └── profile_report*.html
├── src/nurse_epidemic/
│   ├── schemas/columns.py
│   ├── io/loaders.py
│   ├── cleaning/standardize.py
│   ├── cleaning/depara.py
│   ├── pipeline/prepare_data.py
│   └── stats/                        # descriptive, association, correlation
├── tests/
├── data/                             # Ignorado pelo Git (exceto .gitkeep)
└── pyproject.toml
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Documentação

| Recurso | Link |
|---------|------|
| Plano de desenvolvimento | [`docs/plano_de_desenvolvimento.md`](docs/plano_de_desenvolvimento.md) |
| Plano de implementação | [`docs/plano_implementacao_upa.md`](docs/plano_implementacao_upa.md) |
| De-para de normalizações | [`docs/depara_normalizacoes.md`](docs/depara_normalizacoes.md) |
| Guia geral dos reports | [`reports/README.md`](reports/README.md) |
| Como ler tabelas descritivas | [`reports/descriptive/README.md`](reports/descriptive/README.md) |
| Como ler figuras | [`reports/figures/README.md`](reports/figures/README.md) |
| Interpretação das associações | [`reports/association_results.md`](reports/association_results.md) |
| Interpretação das correlações | [`reports/correlation_results.md`](reports/correlation_results.md) |
| Change spec | [`.specs/changes/upa-analytics/`](.specs/changes/upa-analytics/) |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Convenção de Commits

Este projeto segue **Conventional Commits**:

```
<tipo>(<escopo opcional>): <descrição>
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
`chore`, `infra`, `imp`, `breaking`.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Autor

| Nome | Email |
|------|-------|
| **Rodrigo Watanabe Pisaia** | rodrigo.watanabe0107@gmail.com |

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>
