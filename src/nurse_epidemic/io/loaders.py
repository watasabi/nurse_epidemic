"""Leitura de dados UPA."""

from pathlib import Path

import pandas as pd

from nurse_epidemic.schemas.columns import (
    COL_MES_COLETA,
    EXCEL_COL_MAP,
    SHEET_COLUMN_ALIASES,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_EXCEL_PATH = (
    PROJECT_ROOT / "data" / "raw" / "Planilha de dados- Estátistico.xlsx"
)

DROP_COLUMN_PATTERNS = ("Unnamed:",)


def _harmonize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica nomes de colunas entre abas."""
    out = df.copy()
    for alias, canonical in SHEET_COLUMN_ALIASES.items():
        if alias in out.columns and canonical not in out.columns:
            out[canonical] = out[alias]
        if alias in out.columns:
            out = out.drop(columns=[alias])
    return out


def _drop_junk_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove colunas vazias ou sem nome."""
    keep = [
        c
        for c in df.columns
        if str(c).strip() and not str(c).startswith(DROP_COLUMN_PATTERNS)
    ]
    return df[keep]


def load_upa_excel(
    path: Path | str = DEFAULT_EXCEL_PATH,
) -> pd.DataFrame:
    """Lê todas as abas do Excel e concatena pacientes.

    Args:
        path: Caminho ao arquivo Excel.

    Returns:
        DataFrame com colunas renomeadas para snake_case.
    """
    path = Path(path)
    xl = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []

    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        df = _harmonize_columns(df)
        df = _drop_junk_columns(df)
        df[COL_MES_COLETA] = sheet
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    rename_map = {
        k: v for k, v in EXCEL_COL_MAP.items() if k in combined.columns
    }
    return combined.rename(columns=rename_map)
