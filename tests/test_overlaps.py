"""Testes de sobreposição (Venn) e da hierarquia por cores."""

import pandas as pd

from nurse_epidemic.cleaning.standardize import (
    CARDIAC_HIERARCHY,
    apply_group_hierarchy,
    parse_yes_no,
)
from nurse_epidemic.schemas.columns import (
    COL_COR_DOENCAS_CARDIACAS,
    COL_DOENCAS_CARDIACAS,
    COL_ETILISTA,
    COL_HIPERTENSO,
    COL_OUTRA_DOENCA_CARDIACA,
    COL_TABAGISTA,
    COR_HIPERTENSAO,
    COR_OUTRA_CARDIACA,
)
from nurse_epidemic.stats.overlaps import (
    hierarchy_inconsistencies,
    multimorbidity_table,
    nested_group_table,
    venn_regions_table,
    venn_subsets,
)

GREEN = COR_HIPERTENSAO
BLUE = COR_OUTRA_CARDIACA


def _cardiac_frame() -> pd.DataFrame:
    # linha 3: HAS sem marcar cardíaca; linha 4: verde sem HAS
    return pd.DataFrame(
        {
            COL_HIPERTENSO: ["SIM", "NAO", "SIM", "NAO", "NAO", "NAO"],
            COL_DOENCAS_CARDIACAS: ["SIM", "SIM", "NAO", "SIM", "NAO", None],
            COL_COR_DOENCAS_CARDIACAS: [GREEN, BLUE, None, GREEN, None, None],
        }
    )


def test_parse_yes_no_treats_pd_na_as_missing() -> None:
    assert parse_yes_no(pd.NA) is None


def test_hierarchy_puts_every_has_inside_cardiac() -> None:
    out = apply_group_hierarchy(_cardiac_frame(), CARDIAC_HIERARCHY)
    group = out[COL_DOENCAS_CARDIACAS]
    other = out[COL_OUTRA_DOENCA_CARDIACA]
    assert group.iloc[:5].tolist() == ["SIM", "SIM", "SIM", "NAO", "NAO"]
    assert other.iloc[:5].tolist() == ["NAO", "SIM", "NAO", "NAO", "NAO"]
    assert group.iloc[5:].isna().all()
    assert other.iloc[5:].isna().all()


def test_nested_group_table_counts() -> None:
    out = apply_group_hierarchy(_cardiac_frame(), CARDIAC_HIERARCHY)
    table = nested_group_table(
        out, CARDIAC_HIERARCHY, ("Cardíacas", "HAS", "Outras")
    )
    counts = dict(zip(table["categoria"], table["absoluta"]))
    assert counts == {
        "Cardíacas (total)": 3,
        "HAS": 2,
        "Outras": 1,
        "Sem cardíacas": 2,
    }
    assert table["n_valido"].iloc[0] == 5  # noqa: PLR2004


def test_hierarchy_inconsistencies_flags_both_rows() -> None:
    raw = _cardiac_frame()
    qa = hierarchy_inconsistencies(raw, CARDIAC_HIERARCHY)
    assert len(qa) == 2  # noqa: PLR2004


def test_venn_subsets_and_regions() -> None:
    df = pd.DataFrame(
        {
            COL_TABAGISTA: ["SIM", "SIM", "NAO", "NAO", None],
            COL_ETILISTA: ["SIM", "NAO", "SIM", "NAO", "SIM"],
        }
    )
    cols = [COL_TABAGISTA, COL_ETILISTA]
    assert venn_subsets(df, cols) == {"00": 1, "01": 1, "10": 1, "11": 1}
    table = venn_regions_table(
        df, {"Tabagista": COL_TABAGISTA, "Etilista": COL_ETILISTA}
    )
    assert table["combinacao"].iloc[0] == "Tabagista + Etilista"
    assert table["absoluta"].sum() == table["n_valido"].iloc[0] == 4  # noqa: PLR2004


def test_multimorbidity_table() -> None:
    df = pd.DataFrame(
        {
            COL_TABAGISTA: ["SIM", "SIM", "NAO"],
            COL_ETILISTA: ["SIM", "NAO", "NAO"],
        }
    )
    table = multimorbidity_table(df, [COL_TABAGISTA, COL_ETILISTA])
    assert table["n_grupos"].tolist() == [0, 1, 2]
    assert table["absoluta"].tolist() == [1, 1, 1]
