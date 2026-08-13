"""Resumos clínicos agrupados para relatórios UPA."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nurse_epidemic.schemas.columns import (
    COL_DESFECHO_PADRONIZADO,
    COL_DIABETICO,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_METABOLICAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_ETILISTA,
    COL_HIPERTENSO,
    COL_SETOR_DESTINADO,
    COL_TABAGISTA,
    COL_TEMPO_PERMANENCIA,
)
from nurse_epidemic.stats.descriptive import frequency_table

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOENCAS_UPA_PATH = PROJECT_ROOT / "data" / "external" / "doencas_upa.csv"


def desfecho_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência de desfechos padronizados."""
    return frequency_table(df[COL_DESFECHO_PADRONIZADO])


def setor_destinado_table(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência por setor destinado."""
    return frequency_table(df[COL_SETOR_DESTINADO])


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


def doencas_upa_long(path: Path | str = DOENCAS_UPA_PATH) -> pd.DataFrame:
    """Transforma doencas_upa.csv em formato longo para gráficos."""
    path = Path(path)
    raw = pd.read_csv(path)
    id_col = raw.columns[0]
    value_cols = [c for c in raw.columns if c != id_col and "Total" not in c]
    long = raw.melt(
        id_vars=[id_col],
        value_vars=value_cols,
        var_name="periodo_upa",
        value_name="contagem",
    )
    long = long.rename(columns={id_col: "grupo_doenca"})
    return long
