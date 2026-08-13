"""De-para de normalizações: colunas e valores originais → padronizados."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nurse_epidemic.schemas.columns import (
    DEPARA_VALUE_COLS,
    EXCEL_COL_MAP,
    SHEET_COLUMN_ALIASES,
)

# Regras documentadas (valor original → valor normalizado)
VALUE_RULES: dict[str, dict[str, str]] = {
    "sexo": {
        "M / MASCULINO": "M",
        "F / FEMININO": "F",
        "Outros": "OUTRO",
    },
    "sim_nao": {
        "SIM / S / SIM_*": "SIM",
        "NÃO / NAO / N / NEGA": "NAO",
    },
    "desfecho_padronizado": {
        "ALTA*": "ALTA",
        "TRANSFERENCIA* / TRANSFERÊNCIA*": "INTERNAMENTO",
        "CAPS / EVASAO / ENCERRAMENTO*": "ENCAMINHAMENTO",
        "OBITO* / ÓBITO*": "OBITO",
    },
    "tempo_permanencia": {
        "ATÉ 6H (variantes com espaço)": "ATE_6H",
        "ATÉ 12H": "ATE_12H",
        "ATÉ 24H": "ATE_24H",
        "MAIS DE 24H": "MAIS_24H",
    },
    "setor_destinado": {
        "Texto normalizado (maiúsculas, sem acentos)": "valor literal",
    },
}


def column_mapping_table() -> pd.DataFrame:
    """Tabela de-para de nomes de colunas Excel → snake_case."""
    rows: list[dict[str, str]] = []
    seen_targets: set[str] = set()

    for excel_col, col_norm in EXCEL_COL_MAP.items():
        if col_norm in seen_targets:
            alias = "alias"
        else:
            alias = "principal"
            seen_targets.add(col_norm)
        rows.append(
            {
                "coluna_original_excel": excel_col,
                "coluna_normalizada": col_norm,
                "tipo_mapeamento": alias,
                "observacao": "",
            }
        )

    for alias, canonical in SHEET_COLUMN_ALIASES.items():
        rows.append(
            {
                "coluna_original_excel": alias,
                "coluna_normalizada": EXCEL_COL_MAP.get(canonical, canonical),
                "tipo_mapeamento": "alias_aba",
                "observacao": f"Unificado com '{canonical}'",
            }
        )

    rows.append(
        {
            "coluna_original_excel": "(derivada)",
            "coluna_normalizada": "duracao_horas",
            "tipo_mapeamento": "derivada",
            "observacao": ("Calculada: data/hora fim − data/hora início"),
        }
    )
    rows.append(
        {
            "coluna_original_excel": "(derivada)",
            "coluna_normalizada": "desfecho_padronizado",
            "tipo_mapeamento": "derivada",
            "observacao": "Agrupamento de DESFECHO FINAL",
        }
    )

    return pd.DataFrame(rows)


def value_mapping_table(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Tabela de-para valor a valor observado nos dados.

    Args:
        df_raw: DataFrame após load (antes da limpeza de valores).
        df_clean: DataFrame após clean_and_standardize.

    Returns:
        DataFrame com coluna, valor_original, valor_normalizado, n.
    """
    rows: list[dict[str, object]] = []

    for col in DEPARA_VALUE_COLS:
        if col not in df_raw.columns or col not in df_clean.columns:
            continue
        pairs = pd.DataFrame(
            {
                "valor_original": df_raw[col].astype("string"),
                "valor_normalizado": df_clean[col].astype("string"),
            }
        )
        counts = (
            pairs.groupby(
                ["valor_original", "valor_normalizado"],
                dropna=False,
            )
            .size()
            .reset_index(name="n")
        )
        for _, row in counts.iterrows():
            orig = row["valor_original"]
            norm = row["valor_normalizado"]
            rows.append(
                {
                    "coluna_normalizada": col,
                    "valor_original": ("<NA>" if pd.isna(orig) else str(orig)),
                    "valor_normalizado": (
                        "<NA>" if pd.isna(norm) else str(norm)
                    ),
                    "n": int(row["n"]),
                }
            )

    return pd.DataFrame(rows)


def rules_summary_table() -> pd.DataFrame:
    """Regras de normalização em formato tabular."""
    rows: list[dict[str, str]] = []
    for grupo, rules in VALUE_RULES.items():
        for orig, norm in rules.items():
            rows.append(
                {
                    "grupo_regra": grupo,
                    "padrao_original": orig,
                    "valor_normalizado": norm,
                }
            )
    return pd.DataFrame(rows)


def export_depara(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    reports_dir: Path | str,
    docs_dir: Path | str,
) -> list[Path]:
    """Exporta de-para em CSV e Markdown.

    Args:
        df_raw: Dados carregados (renomeados, não limpos).
        df_clean: Dados limpos.
        reports_dir: Destino dos CSVs.
        docs_dir: Destino do Markdown legível.

    Returns:
        Lista de arquivos gerados.
    """
    reports_dir = Path(reports_dir)
    docs_dir = Path(docs_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    col_table = column_mapping_table()
    val_table = value_mapping_table(df_raw, df_clean)
    rules_table = rules_summary_table()

    paths: list[Path] = []

    col_path = reports_dir / "depara_colunas.csv"
    col_table.to_csv(col_path, index=False)
    paths.append(col_path)

    val_path = reports_dir / "depara_valores.csv"
    val_table.to_csv(val_path, index=False)
    paths.append(val_path)

    rules_path = reports_dir / "depara_regras.csv"
    rules_table.to_csv(rules_path, index=False)
    paths.append(rules_path)

    md_path = docs_dir / "depara_normalizacoes.md"
    md_path.write_text(
        _render_markdown(col_table, val_table, rules_table),
        encoding="utf-8",
    )
    paths.append(md_path)

    return paths


def _render_markdown(
    col_table: pd.DataFrame,
    val_table: pd.DataFrame,
    rules_table: pd.DataFrame,
) -> str:
    """Gera documentação legível do de-para."""
    lines = [
        "# De-para de normalizações — UPA Curitiba",
        "",
        "Este documento descreve como os dados originais da planilha "
        "foram renomeados e padronizados. Os CSVs espelham estas "
        "tabelas em `reports/depara_*.csv`.",
        "",
        "## 1. Colunas (Excel → snake_case)",
        "",
        _df_to_md(col_table),
        "",
        "## 2. Regras de normalização de valores",
        "",
        _df_to_md(rules_table),
        "",
        "## 3. Valores observados (original → normalizado)",
        "",
    ]

    for col in val_table["coluna_normalizada"].unique():
        subset = val_table[val_table["coluna_normalizada"] == col]
        lines.append(f"### `{col}`")
        lines.append("")
        lines.append(_df_to_md(subset))
        lines.append("")

    return "\n".join(lines)


def _df_to_md(df: pd.DataFrame) -> str:
    """Converte DataFrame pequeno em tabela Markdown."""
    if df.empty:
        return "_Sem registros._"
    headers = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    body = [
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in df.astype(str).values
    ]
    return "\n".join([headers, sep, *body])
