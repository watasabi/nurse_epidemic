"""Testes de associação bi-variados."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from phik import phik_matrix
from scipy import stats

from nurse_epidemic.cleaning.standardize import simplify_for_association
from nurse_epidemic.schemas.columns import (
    ASSOCIATION_PREDICTORS,
    COL_DESFECHO_PADRONIZADO,
    COL_DURACAO_HORAS,
)

FISHER_MIN_CELL = 5
MIN_GROUPS = 2


@dataclass
class AssociationResult:
    """Resultado de um teste de associação."""

    variable: str
    target: str
    test: str
    statistic: float
    p_value: float
    n: int
    note: str | None = None


def _crosstab_clean(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
) -> pd.DataFrame:
    """Crosstab sem valores nulos."""
    subset = df[[col_a, col_b]].dropna()
    return pd.crosstab(subset[col_a], subset[col_b])


def chi_square_or_fisher(
    df: pd.DataFrame,
    predictor: str,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> AssociationResult:
    """Teste χ² ou Fisher para associação categórica × categórica."""
    table = _crosstab_clean(df, predictor, target)
    n = int(table.values.sum())

    if table.shape == (0, 0) or n == 0:
        return AssociationResult(
            variable=predictor,
            target=target,
            test="none",
            statistic=0.0,
            p_value=1.0,
            n=0,
            note="sem dados",
        )

    use_fisher = table.shape == (MIN_GROUPS, MIN_GROUPS) and (
        table.values.min() < FISHER_MIN_CELL
    )
    if use_fisher:
        _, p_value = stats.fisher_exact(table.values)
        return AssociationResult(
            variable=predictor,
            target=target,
            test="fisher_exact",
            statistic=0.0,
            p_value=float(p_value),
            n=n,
            note="células < 5",
        )

    chi2, p_value, _, _ = stats.chi2_contingency(table.values)
    return AssociationResult(
        variable=predictor,
        target=target,
        test="chi2",
        statistic=float(chi2),
        p_value=float(p_value),
        n=n,
    )


def continuous_vs_categorical(
    df: pd.DataFrame,
    predictor: str,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> AssociationResult:
    """Compara variável contínua entre grupos categóricos."""
    subset = df[[predictor, target]].copy()
    subset[predictor] = pd.to_numeric(subset[predictor], errors="coerce")
    subset = subset.dropna()

    groups = [
        g[predictor].values for _, g in subset.groupby(target, observed=True)
    ]
    n = sum(len(g) for g in groups)

    if len(groups) < MIN_GROUPS:
        return AssociationResult(
            variable=predictor,
            target=target,
            test="none",
            statistic=0.0,
            p_value=1.0,
            n=n,
            note="grupos insuficientes",
        )

    if len(groups) == MIN_GROUPS:
        stat, p_value = stats.mannwhitneyu(
            groups[0], groups[1], alternative="two-sided"
        )
        test_name = "mannwhitneyu"
    else:
        stat, p_value = stats.kruskal(*groups)
        test_name = "kruskal"

    return AssociationResult(
        variable=predictor,
        target=target,
        test=test_name,
        statistic=float(stat),
        p_value=float(p_value),
        n=n,
    )


def run_association_battery(
    df: pd.DataFrame,
    predictors: list[str],
    target: str = COL_DESFECHO_PADRONIZADO,
    numeric_predictors: list[str] | None = None,
) -> pd.DataFrame:
    """Executa battery de testes de associação com o desfecho."""
    work = df.copy()
    numeric_set = set(numeric_predictors or [])

    for col in predictors:
        if col not in numeric_set and col in work.columns:
            work[col] = work[col].map(simplify_for_association)

    results: list[AssociationResult] = []

    for col in predictors:
        if col not in work.columns:
            continue
        if col in numeric_set:
            results.append(continuous_vs_categorical(work, col, target))
        else:
            results.append(chi_square_or_fisher(work, col, target))

    return pd.DataFrame([r.__dict__ for r in results])


def phik_association_matrix(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    *,
    target: str = COL_DESFECHO_PADRONIZADO,
    numeric_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Calcula matriz de associação PhiK."""
    predictors = columns or list(ASSOCIATION_PREDICTORS)
    interval = list(numeric_cols or [COL_DURACAO_HORAS])
    numeric_set = set(interval)
    selected = [c for c in predictors if c in df.columns]
    if target in df.columns and target not in selected:
        selected.append(target)

    work = df[selected].copy()
    for col in selected:
        if col in numeric_set:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        else:
            work[col] = work[col].map(simplify_for_association)
            work[col] = work[col].astype(object)

    interval_present = [c for c in interval if c in work.columns]
    return phik_matrix(work, interval_cols=interval_present)
