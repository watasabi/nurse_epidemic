"""Testes de associação."""

import pandas as pd

from nurse_epidemic.stats.association import chi_square_or_fisher

MIN_ASSOC_N = 6


def test_chi_square_or_fisher_runs() -> None:
    df = pd.DataFrame(
        {
            "tabagista": ["SIM", "NAO", "SIM", "NAO", "SIM", "NAO"],
            "desfecho_padronizado": [
                "ALTA",
                "ALTA",
                "INTERNAMENTO",
                "ALTA",
                "INTERNAMENTO",
                "ALTA",
            ],
        }
    )
    result = chi_square_or_fisher(df, "tabagista", "desfecho_padronizado")
    assert result.n == MIN_ASSOC_N
    assert result.p_value >= 0.0
