"""Resumos clínicos agrupados para relatórios UPA."""

from __future__ import annotations

import pandas as pd

from nurse_epidemic.schemas.columns import (
    COL_DESFECHO_PADRONIZADO,
    COL_DIABETICO,
    COL_DISCRIMINADOR,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_METABOLICAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_ETILISTA,
    COL_FLUXOGRAMA,
    COL_HIPERTENSO,
    COL_SETOR_DESTINADO,
    COL_TABAGISTA,
    COL_TEMPO_PERMANENCIA,
)
from nurse_epidemic.stats.descriptive import frequency_table


def desfecho_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência de desfechos padronizados."""
    return frequency_table(df[COL_DESFECHO_PADRONIZADO])


def setor_destinado_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência por setor destinado."""
    return frequency_table(df[COL_SETOR_DESTINADO])


def fluxograma_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência dos fluxogramas de classificação de risco."""
    return frequency_table(df[COL_FLUXOGRAMA])


def discriminador_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência dos discriminadores de classificação de risco."""
    return frequency_table(df[COL_DISCRIMINADOR])


def tempo_permanencia_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência por tempo de permanência."""
    return frequency_table(df[COL_TEMPO_PERMANENCIA])


def comorbidades_table(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de comorbidades individuais (SIM/NAO)."""
    cols = [
        COL_DIABETICO,
        COL_HIPERTENSO,
        COL_DOENCAS_CARDIACAS,
        COL_DOENCAS_RESPIRATORIAS,
        COL_DOENCAS_METABOLICAS,
    ]
    rows: list[dict[str, object]] = []
    for col in cols:
        if col not in df.columns:
            continue
        sim = (df[col] == "SIM").sum()
        total = df[col].notna().sum()
        rows.append(
            {
                "comorbidade": col,
                "sim_absoluta": int(sim),
                "sim_relativa": sim / total if total else 0.0,
                "n_valido": int(total),
            }
        )
    return pd.DataFrame(rows)


def habitos_vida_table(df: pd.DataFrame) -> pd.DataFrame:
    """Tabagismo e etilismo."""
    rows: list[dict[str, object]] = []
    for col, label in [
        (COL_TABAGISTA, "tabagista"),
        (COL_ETILISTA, "etilista"),
    ]:
        if col not in df.columns:
            continue
        sim = (df[col] == "SIM").sum()
        total = df[col].notna().sum()
        rows.append(
            {
                "habito": label,
                "sim_absoluta": int(sim),
                "sim_relativa": sim / total if total else 0.0,
                "n_valido": int(total),
            }
        )
    return pd.DataFrame(rows)
