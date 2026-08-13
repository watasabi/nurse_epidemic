"""Correlações Pearson/Spearman com intervalo de confiança 95%."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from nurse_epidemic.schemas.columns import COL_DURACAO_HORAS, COL_FAIXA_ETARIA

FAIXA_ORDINAL: dict[str, int] = {
    "18-40": 1,
    "40-60": 2,
    "60-80": 3,
    "80-100": 4,
}

SHAPIRO_MAX_N = 5000
BOOTSTRAP_N = 1000
ALPHA = 0.05
MIN_CORR_N = 3
MIN_CI_N = 4


def _fisher_ci(r: float, n: int) -> tuple[float, float]:
    """IC 95% para Pearson via transformação Fisher z."""
    if n < MIN_CI_N or abs(r) >= 1.0:
        return (float("nan"), float("nan"))
    z = math.atanh(r)
    se = 1 / math.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - ALPHA / 2)
    lo = math.tanh(z - z_crit * se)
    hi = math.tanh(z + z_crit * se)
    return (lo, hi)


def _bootstrap_spearman_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int = BOOTSTRAP_N,
) -> tuple[float, float]:
    """IC 95% bootstrap para Spearman."""
    rng = np.random.default_rng(42)
    n = len(x)
    if n < MIN_CI_N:
        return (float("nan"), float("nan"))
    rhos: list[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        rho, _ = stats.spearmanr(x[idx], y[idx])
        if not math.isnan(rho):
            rhos.append(float(rho))
    if not rhos:
        return (float("nan"), float("nan"))
    lo, hi = np.percentile(rhos, [2.5, 97.5])
    return (float(lo), float(hi))


def pearson_spearman_pair(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
) -> dict[str, object]:
    """Calcula correlação entre duas variáveis numéricas.

    Usa Pearson se ambas passarem Shapiro (n≤5000); senão Spearman.
    """
    subset = df[[col_a, col_b]].copy()
    subset[col_a] = pd.to_numeric(subset[col_a], errors="coerce")
    subset[col_b] = pd.to_numeric(subset[col_b], errors="coerce")
    subset = subset.dropna()
    n = len(subset)

    if n < MIN_CORR_N:
        return {
            "variable_a": col_a,
            "variable_b": col_b,
            "method": "none",
            "r": float("nan"),
            "ci_lower": float("nan"),
            "ci_upper": float("nan"),
            "p_value": float("nan"),
            "n": n,
        }

    x = subset[col_a].values
    y = subset[col_b].values

    use_pearson = n <= SHAPIRO_MAX_N
    if use_pearson:
        _, p_a = stats.shapiro(x)
        _, p_b = stats.shapiro(y)
        use_pearson = p_a > ALPHA and p_b > ALPHA

    if use_pearson:
        r, p_value = stats.pearsonr(x, y)
        ci_lo, ci_hi = _fisher_ci(float(r), n)
        method = "pearson"
    else:
        r, p_value = stats.spearmanr(x, y)
        ci_lo, ci_hi = _bootstrap_spearman_ci(x, y)
        method = "spearman"

    return {
        "variable_a": col_a,
        "variable_b": col_b,
        "method": method,
        "r": float(r),
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "p_value": float(p_value),
        "n": n,
    }


def run_correlation_battery(df: pd.DataFrame) -> pd.DataFrame:
    """Executa correlações entre variáveis numéricas disponíveis."""
    work = df.copy()
    if COL_FAIXA_ETARIA in work.columns:
        work["faixa_etaria_ordinal"] = work[COL_FAIXA_ETARIA].map(
            FAIXA_ORDINAL
        )

    numeric_cols = [COL_DURACAO_HORAS, "faixa_etaria_ordinal"]
    numeric_cols = [c for c in numeric_cols if c in work.columns]

    pairs: list[tuple[str, str]] = []
    for i, a in enumerate(numeric_cols):
        for b in numeric_cols[i + 1 :]:
            pairs.append((a, b))

    results = [pearson_spearman_pair(work, a, b) for a, b in pairs]
    return pd.DataFrame(results)
