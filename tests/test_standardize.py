"""Testes de padronização."""

import pandas as pd

from nurse_epidemic.cleaning.depara import (
    column_mapping_table,
    value_mapping_table,
)
from nurse_epidemic.cleaning.standardize import (
    clean_and_standardize,
    compute_duracao_horas,
    parse_yes_no,
    standardize_desfecho_upa,
    standardize_genero,
    standardize_tempo_permanencia,
)
from nurse_epidemic.schemas.columns import (
    COL_DATA_FIM,
    COL_DATA_INICIO,
    COL_DESFECHO_PADRONIZADO,
    COL_DURACAO_HORAS,
    COL_HORA_FIM,
    COL_HORA_INICIO,
    COL_TEMPO_PERMANENCIA,
)


def test_parse_yes_no() -> None:
    assert parse_yes_no("SIM") == "SIM"
    assert parse_yes_no("NÃO") == "NAO"
    assert parse_yes_no("NAO ") == "NAO"


def test_standardize_genero() -> None:
    assert standardize_genero("M") == "M"
    assert standardize_genero("F ") == "F"


def test_standardize_desfecho_upa() -> None:
    assert standardize_desfecho_upa("ALTA.") == "ALTA"
    assert (
        standardize_desfecho_upa("TRANSFERÊNCIA HOSPITALAR.") == "INTERNAMENTO"
    )
    assert standardize_desfecho_upa("CAPS.") == "ENCAMINHAMENTO"
    assert (
        standardize_desfecho_upa("TRANSFERÊNCIA HOSPITALAR- ÓBITO RECENTE.")
        == "OBITO"
    )


def test_standardize_tempo_permanencia() -> None:
    assert standardize_tempo_permanencia("ATÉ 6H ") == "ATE_6H"
    assert standardize_tempo_permanencia("MAIS DE 24H") == "MAIS_24H"


def test_compute_duracao_horas() -> None:
    df = pd.DataFrame(
        {
            COL_DATA_INICIO: ["03/04/2025"],
            COL_HORA_INICIO: ["14:17:02"],
            COL_DATA_FIM: ["03/04/2025"],
            COL_HORA_FIM: ["14:22:28"],
        }
    )
    dur = compute_duracao_horas(df)
    assert dur.iloc[0] > 0


def test_clean_adds_derived_columns() -> None:
    raw = pd.DataFrame(
        {
            "sexo": ["M"],
            "desfecho": ["ALTA."],
            COL_TEMPO_PERMANENCIA: ["ATÉ 6H"],
            COL_DATA_INICIO: ["03/04/2025"],
            COL_HORA_INICIO: ["14:17:02"],
            COL_DATA_FIM: ["03/04/2025"],
            COL_HORA_FIM: ["14:22:28"],
        }
    )
    clean = clean_and_standardize(raw)
    assert COL_DESFECHO_PADRONIZADO in clean.columns
    assert COL_DURACAO_HORAS in clean.columns
    assert clean[COL_DESFECHO_PADRONIZADO].iloc[0] == "ALTA"


def test_depara_tables() -> None:
    raw = pd.DataFrame({"sexo": ["M", "F"], "desfecho": ["ALTA.", "CAPS."]})
    clean = clean_and_standardize(raw)
    col_map = column_mapping_table()
    assert not col_map.empty
    val_map = value_mapping_table(raw, clean)
    assert not val_map.empty
