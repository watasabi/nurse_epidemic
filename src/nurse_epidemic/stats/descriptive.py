"""Estatística descritiva para o dataset UPA."""

from pathlib import Path

import pandas as pd

from nurse_epidemic.schemas.columns import (
    CLINICAL_CATEGORICAL_COLS,
    CLINICAL_NUMERIC_COLS,
    DEMOGRAPHIC_COLS,
)


def frequency_table(
    series: pd.Series,
    dropna: bool = True,
) -> pd.DataFrame:
    """Tabela de frequência absoluta e relativa."""
    counts = series.value_counts(dropna=dropna)
    total = counts.sum()
    return pd.DataFrame(
        {
            "valor": counts.index.astype(str),
            "absoluta": counts.values,
            "relativa": counts.values / total,
        }
    )


def numeric_summary(series: pd.Series) -> pd.DataFrame:
    """Resumo de variável quantitativa."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    return pd.DataFrame(
        {
            "n": [len(clean)],
            "media": [clean.mean()],
            "mediana": [clean.median()],
            "min": [clean.min()],
            "max": [clean.max()],
            "desvio_padrao": [clean.std(ddof=1) if len(clean) > 1 else 0.0],
        }
    )


def descriptive_report(
    df: pd.DataFrame,
    categorical_cols: list[str] | None = None,
    numeric_cols: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Gera tabelas descritivas para colunas categóricas e numéricas."""
    cat_cols = categorical_cols or []
    num_cols = numeric_cols or []
    report: dict[str, pd.DataFrame] = {}

    for col in cat_cols:
        if col in df.columns:
            report[col] = frequency_table(df[col])

    for col in num_cols:
        if col in df.columns:
            report[col] = numeric_summary(df[col])

    return report


def demographic_report(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabelas descritivas demográficas."""
    return descriptive_report(
        df,
        categorical_cols=[COL for COL in DEMOGRAPHIC_COLS],
        numeric_cols=[],
    )


def clinical_report(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabelas descritivas clínicas."""
    return descriptive_report(
        df,
        categorical_cols=CLINICAL_CATEGORICAL_COLS,
        numeric_cols=CLINICAL_NUMERIC_COLS,
    )


def export_report(
    report: dict[str, pd.DataFrame],
    output_dir: Path | str,
    prefix: str = "",
) -> list[Path]:
    """Exporta tabelas descritivas como CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for name, table in report.items():
        path = output_dir / f"{prefix}{name}.csv"
        table.to_csv(path, index=False)
        paths.append(path)

    return paths
