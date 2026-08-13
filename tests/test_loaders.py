"""Testes do loader UPA."""

from pathlib import Path

from nurse_epidemic.io.loaders import DEFAULT_EXCEL_PATH, load_upa_excel
from nurse_epidemic.schemas.columns import (
    COL_COMORBIDADE,
    COL_DESFECHO,
    COL_SEXO,
)

EXPECTED_ROWS = 328


def test_load_upa_excel_row_count() -> None:
    if not Path(DEFAULT_EXCEL_PATH).exists():
        return
    df = load_upa_excel()
    assert len(df) == EXPECTED_ROWS


def test_harmonized_columns() -> None:
    if not Path(DEFAULT_EXCEL_PATH).exists():
        return
    df = load_upa_excel()
    assert COL_SEXO in df.columns
    assert COL_DESFECHO in df.columns
    assert COL_COMORBIDADE in df.columns
    assert "mes_coleta" in df.columns
