"""Sobreposição entre comorbidades e hábitos (tabelas para Venn)."""

from __future__ import annotations

from itertools import product

import pandas as pd

from nurse_epidemic.cleaning.standardize import GroupHierarchy
from nurse_epidemic.schemas.columns import COL_LINHA_EXCEL, COL_MES_COLETA


def venn_subsets(df: pd.DataFrame, cols: list[str]) -> dict[str, int]:
    """Conta pacientes em cada região exclusiva de um diagrama de Venn.

    Considera só pacientes com resposta em todas as ``cols``.

    Args:
        df: DataFrame com colunas SIM/NAO.
        cols: Conjuntos do diagrama, na ordem desejada (2 ou 3).

    Returns:
        Dicionário no formato do matplotlib-venn: chave ``"101"`` =
        SIM no 1º e 3º conjuntos e NAO no 2º; ``"000"`` = nenhum.
    """
    valid = df[cols].dropna()
    flags = valid.astype("object").eq("SIM")
    keys = flags.apply(
        lambda row: "".join("1" if v else "0" for v in row), axis=1
    )
    counts = keys.value_counts()
    return {
        "".join(bits): int(counts.get("".join(bits), 0))
        for bits in product("01", repeat=len(cols))
    }


def venn_regions_table(df: pd.DataFrame, sets: dict[str, str]) -> pd.DataFrame:
    """Tabela das regiões exclusivas de um diagrama de Venn.

    Cada paciente aparece em exatamente uma linha, então a soma de
    ``absoluta`` é o total de pacientes com informação completa.

    Args:
        df: DataFrame com colunas SIM/NAO.
        sets: Rótulo legível → coluna (ex.: {"Tabagista": "tabagista"}).

    Returns:
        DataFrame com ``combinacao``, ``n_condicoes``, ``absoluta``,
        ``relativa`` e ``n_valido``, das combinações mais complexas
        (todas as condições) para "nenhuma".
    """
    labels = list(sets)
    subsets = venn_subsets(df, list(sets.values()))
    n_valid = sum(subsets.values())
    rows: list[dict[str, object]] = []
    for key, count in subsets.items():
        present = [lab for lab, bit in zip(labels, key) if bit == "1"]
        if not present:
            name = "Nenhuma das condições"
        elif len(present) == 1:
            name = f"Somente {present[0]}"
        else:
            name = " + ".join(present)
        rows.append(
            {
                "combinacao": name,
                "n_condicoes": len(present),
                "absoluta": count,
                "relativa": count / n_valid if n_valid else 0.0,
                "n_valido": n_valid,
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(
        ["n_condicoes", "absoluta"], ascending=[False, False]
    ).reset_index(drop=True)


def nested_group_table(
    df: pd.DataFrame,
    spec: GroupHierarchy,
    labels: tuple[str, str, str],
) -> pd.DataFrame:
    """Decompõe um grupo de doenças em "específica" + "outras".

    Ex.: doenças cardíacas = hipertensão (verde) + outra doença
    cardíaca sem hipertensão (azul). Os hipertensos podem ter outra
    doença cardíaca associada; a planilha não distingue esse caso.

    Args:
        df: DataFrame limpo (após ``apply_group_hierarchy``).
        spec: Colunas do grupo.
        labels: (grupo, específica, outras) para as linhas da tabela.

    Returns:
        DataFrame com ``categoria``, ``absoluta``, ``relativa`` (sobre
        todos os pacientes com informação) e ``relativa_grupo`` (sobre
        o total do grupo).
    """
    group_label, specific_label, other_label = labels
    valid = df[df[spec.group_col].notna()]
    n_valid = len(valid)
    is_yes = valid[[spec.group_col, spec.specific_col, spec.other_col]]
    is_yes = is_yes.astype("object").eq("SIM")
    n_group = int(is_yes[spec.group_col].sum())
    in_group = [
        (f"{group_label} (total)", n_group),
        (specific_label, int(is_yes[spec.specific_col].sum())),
        (other_label, int(is_yes[spec.other_col].sum())),
    ]
    rows = [
        {
            "categoria": name,
            "absoluta": count,
            "relativa": count / n_valid if n_valid else 0.0,
            "relativa_grupo": count / n_group if n_group else 0.0,
            "n_valido": n_valid,
        }
        for name, count in in_group
    ]
    rows.append(
        {
            "categoria": f"Sem {group_label.lower()}",
            "absoluta": n_valid - n_group,
            "relativa": (n_valid - n_group) / n_valid if n_valid else 0.0,
            "relativa_grupo": None,
            "n_valido": n_valid,
        }
    )
    return pd.DataFrame(rows)


def multimorbidity_table(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Quantos grupos de comorbidade cada paciente acumula.

    Args:
        df: DataFrame com colunas SIM/NAO.
        cols: Grupos de comorbidade considerados.

    Returns:
        DataFrame com ``n_grupos`` (0, 1, 2, …), ``absoluta``,
        ``relativa`` e ``n_valido``.
    """
    valid = df[cols].dropna()
    n_groups = valid.astype("object").eq("SIM").sum(axis=1)
    counts = n_groups.value_counts().sort_index()
    n_valid = len(valid)
    return pd.DataFrame(
        {
            "n_grupos": counts.index.astype(int),
            "absoluta": counts.to_numpy(dtype=int),
            "relativa": counts.to_numpy() / n_valid if n_valid else 0.0,
            "n_valido": n_valid,
        }
    )


def hierarchy_inconsistencies(
    raw: pd.DataFrame,
    spec: GroupHierarchy,
    extra_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Linhas em que a marcação por cor contradiz as colunas SIM/NAO.

    Deve receber os valores **antes** de ``apply_group_hierarchy``
    (SIM/NAO já padronizados), para enxergar o que está na planilha.

    Args:
        raw: DataFrame com SIM/NAO padronizados e coluna de cor.
        spec: Grupo a verificar.
        extra_cols: Colunas extras para ajudar a achar o paciente.

    Returns:
        DataFrame com aba, linha do Excel, problema e valores.
    """
    specific = raw[spec.specific_col].astype("object").eq("SIM")
    group = raw[spec.group_col].astype("object").eq("SIM")
    color = raw[spec.color_col].astype("object")
    checks = {
        f"{spec.specific_col} = SIM, mas {spec.group_col} não é SIM": (
            specific & ~group
        ),
        f"{spec.group_col} com a cor de {spec.specific_col}, "
        f"mas {spec.specific_col} não é SIM": (
            color.eq(spec.specific_color) & ~specific
        ),
        f"{spec.group_col} com a cor de 'outra', "
        f"mas {spec.specific_col} = SIM": (
            color.eq(spec.other_color) & specific
        ),
        f"{spec.group_col} = SIM sem cor de classificação": (
            group & ~color.isin([spec.specific_color, spec.other_color])
        ),
    }
    keep = [
        COL_MES_COLETA,
        COL_LINHA_EXCEL,
        spec.specific_col,
        spec.group_col,
        spec.color_col,
        *(extra_cols or []),
    ]
    keep = [c for c in keep if c in raw.columns]
    frames = [
        raw.loc[mask.fillna(False), keep].assign(problema=problem)
        for problem, mask in checks.items()
        if mask.fillna(False).any()
    ]
    if not frames:
        return pd.DataFrame(columns=[*keep, "problema"])
    return pd.concat(frames, ignore_index=True)
