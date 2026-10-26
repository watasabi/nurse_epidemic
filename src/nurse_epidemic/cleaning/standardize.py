"""Normalização e limpeza do dataset UPA."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from nurse_epidemic.schemas.columns import (
    COL_COR_DOENCAS_CARDIACAS,
    COL_COR_DOENCAS_METABOLICAS,
    COL_DATA_FIM,
    COL_DATA_INICIO,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
    COL_DIABETICO,
    COL_DISCRIMINADOR,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_METABOLICAS,
    COL_DURACAO_HORAS,
    COL_FAIXA_ETARIA,
    COL_FLUXOGRAMA,
    COL_HIPERTENSO,
    COL_HORA_FIM,
    COL_HORA_INICIO,
    COL_IDADE_NUMERICA,
    COL_OUTRA_DOENCA_CARDIACA,
    COL_OUTRA_DOENCA_METABOLICA,
    COL_SETOR_DESTINADO,
    COL_SEXO,
    COL_TEMPO_PERMANENCIA,
    COR_DIABETES,
    COR_HIPERTENSAO,
    COR_OUTRA_CARDIACA,
    COR_OUTRA_METABOLICA,
    YES_NO_COLS,
)

YES_TOKENS = frozenset({"SIM", "S"})
NO_TOKENS = frozenset({"NAO", "NÃO", "N", "NEGA", "NEGOU"})
MAX_LABEL_LEN = 50


def normalize_text(value: object) -> str | None:
    """Normaliza texto: trim, maiúsculas, sem acentos."""
    if (
        value is None
        or value is pd.NA
        or (isinstance(value, float) and pd.isna(value))
    ):
        return None
    text = str(value).strip().rstrip(".")
    if not text or text == ".":
        return None
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\s+", " ", text).strip()
    return text.upper()


def parse_yes_no(value: object) -> str | None:
    """Converte respostas SIM/NAO em categoria padronizada."""
    text = normalize_text(value)
    if text is None:
        return None
    if text in YES_TOKENS or text.startswith("SIM"):
        return "SIM"
    if text in NO_TOKENS or text.startswith("NAO"):
        return "NAO"
    return text


def standardize_genero(value: object) -> str | None:
    """Padroniza gênero em M/F/OUTRO."""
    text = normalize_text(value)
    if text is None:
        return None
    if text in {"M", "MASCULINO"}:
        return "M"
    if text in {"F", "FEMININO"}:
        return "F"
    return "OUTRO"


def standardize_faixa_etaria(value: object) -> str | None:
    """Padroniza faixa etária."""
    text = normalize_text(value)
    if text is None:
        return None
    return text.replace(" ", "")


def standardize_desfecho_upa(value: object) -> str | None:
    """Padroniza desfecho em ALTA/INTERNAMENTO/ENCAMINHAMENTO/OBITO."""
    text = normalize_text(value)
    if text is None:
        return None
    if "OBITO" in text or "ÓBITO" in str(value).upper():
        return "OBITO"
    if text.startswith("ALTA"):
        return "ALTA"
    if "TRANSFEREN" in text:
        return "INTERNAMENTO"
    if any(k in text for k in ("CAPS", "EVASAO", "ENCERRAMENTO")):
        return "ENCAMINHAMENTO"
    return "OUTRO"


def standardize_tempo_permanencia(value: object) -> str | None:
    """Padroniza categorias de tempo de permanência."""
    text = normalize_text(value)
    if text is None:
        return None
    text = text.replace(" ", "")
    if text.startswith("ATE6H") or text == "ATE6H":
        return "ATE_6H"
    if text.startswith("ATE12H"):
        return "ATE_12H"
    if text.startswith("ATE24H"):
        return "ATE_24H"
    if "MAISDE24H" in text or text.startswith("MAISDE24"):
        return "MAIS_24H"
    return text


def parse_date(value: object) -> pd.Timestamp | None:
    """Converte datas mistas em Timestamp."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return pd.Timestamp(value)
    if isinstance(value, pd.Timestamp):
        return value
    text = str(value).strip().rstrip(".")
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        parsed = pd.to_datetime(text, errors="coerce")
    else:
        parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def compute_duracao_horas(df: pd.DataFrame) -> pd.Series:
    """Calcula duração em horas a partir de data/hora início e fim."""
    required = [
        COL_DATA_INICIO,
        COL_HORA_INICIO,
        COL_DATA_FIM,
        COL_HORA_FIM,
    ]
    if not all(col in df.columns for col in required):
        return pd.Series([pd.NA] * len(df), index=df.index)

    start = pd.to_datetime(
        df[COL_DATA_INICIO].astype(str)
        + " "
        + df[COL_HORA_INICIO].astype(str),
        dayfirst=True,
        errors="coerce",
    )
    end = pd.to_datetime(
        df[COL_DATA_FIM].astype(str) + " " + df[COL_HORA_FIM].astype(str),
        dayfirst=True,
        errors="coerce",
    )
    return (end - start).dt.total_seconds() / 3600


def simplify_for_association(value: object) -> str | None:
    """Simplifica variáveis categóricas para testes de associação."""
    text = normalize_text(value)
    if text is None:
        return None
    flag = parse_yes_no(text)
    if flag in {"SIM", "NAO"}:
        return flag
    return text[:MAX_LABEL_LEN] if len(text) > MAX_LABEL_LEN else text


def _is_value(series: pd.Series, value: str) -> pd.Series:
    """Compara com ``value`` tratando ausentes como False."""
    return series.astype("object").eq(value).fillna(False).astype(bool)


@dataclass(frozen=True)
class GroupHierarchy:
    """Grupo de doenças composto por uma doença específica + "outras".

    Na planilha, a célula do grupo (ex.: doenças cardíacas) é pintada de
    uma cor quando a doença específica (ex.: hipertensão) está presente
    e de outra cor (``other_color``) quando há outra doença do grupo sem
    a específica.
    """

    group_col: str
    specific_col: str
    color_col: str
    specific_color: str
    other_color: str
    other_col: str


CARDIAC_HIERARCHY = GroupHierarchy(
    group_col=COL_DOENCAS_CARDIACAS,
    specific_col=COL_HIPERTENSO,
    color_col=COL_COR_DOENCAS_CARDIACAS,
    specific_color=COR_HIPERTENSAO,
    other_color=COR_OUTRA_CARDIACA,
    other_col=COL_OUTRA_DOENCA_CARDIACA,
)
METABOLIC_HIERARCHY = GroupHierarchy(
    group_col=COL_DOENCAS_METABOLICAS,
    specific_col=COL_DIABETICO,
    color_col=COL_COR_DOENCAS_METABOLICAS,
    specific_color=COR_DIABETES,
    other_color=COR_OUTRA_METABOLICA,
    other_col=COL_OUTRA_DOENCA_METABOLICA,
)


def apply_group_hierarchy(
    df: pd.DataFrame, spec: GroupHierarchy
) -> pd.DataFrame:
    """Recompõe um grupo de doenças a partir da marcação por cores.

    - ``other_col`` = SIM quando a célula do grupo tem ``other_color``;
    - ``group_col`` = SIM quando ``specific_col`` ou ``other_col`` é SIM
      (todo hipertenso entra em cardíacas, todo diabético em
      metabólicas); NAO caso contrário.

    Linhas sem resposta no grupo continuam ausentes.

    Args:
        df: DataFrame com colunas SIM/NAO já padronizadas.
        spec: Colunas e cor que definem o grupo.

    Returns:
        Cópia do DataFrame com ``group_col`` e ``other_col`` ajustadas.
    """
    out = df.copy()
    needed = {spec.group_col, spec.specific_col, spec.color_col}
    if not needed <= set(out.columns):
        return out
    has_specific = _is_value(out[spec.specific_col], "SIM")
    answered = out[spec.group_col].notna() | has_specific
    is_other = _is_value(out[spec.color_col], spec.other_color)
    yes_no = {True: "SIM", False: "NAO"}
    out[spec.other_col] = is_other.map(yes_no)
    out[spec.group_col] = (has_specific | is_other).map(yes_no)
    out.loc[~answered, [spec.other_col, spec.group_col]] = None
    return out


def clean_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpeza e padronização ao dataset UPA.

    Args:
        df: DataFrame bruto após load_upa_excel.

    Returns:
        DataFrame limpo pronto para análise.
    """
    out = df.copy()

    if COL_SEXO in out.columns:
        out[COL_SEXO] = out[COL_SEXO].map(standardize_genero)

    if COL_FAIXA_ETARIA in out.columns:
        out[COL_FAIXA_ETARIA] = out[COL_FAIXA_ETARIA].map(
            standardize_faixa_etaria
        )

    if COL_IDADE_NUMERICA in out.columns:
        out[COL_IDADE_NUMERICA] = pd.to_numeric(
            out[COL_IDADE_NUMERICA], errors="coerce"
        )

    for col in YES_NO_COLS:
        if col in out.columns:
            out[col] = out[col].map(parse_yes_no)

    if COL_SETOR_DESTINADO in out.columns:
        out[COL_SETOR_DESTINADO] = out[COL_SETOR_DESTINADO].map(normalize_text)

    if COL_FLUXOGRAMA in out.columns:
        out[COL_FLUXOGRAMA] = out[COL_FLUXOGRAMA].map(normalize_text)

    if COL_DISCRIMINADOR in out.columns:
        out[COL_DISCRIMINADOR] = out[COL_DISCRIMINADOR].map(normalize_text)

    if COL_TEMPO_PERMANENCIA in out.columns:
        out[COL_TEMPO_PERMANENCIA] = out[COL_TEMPO_PERMANENCIA].map(
            standardize_tempo_permanencia
        )

    if COL_DESFECHO in out.columns:
        out[COL_DESFECHO] = out[COL_DESFECHO].map(normalize_text)
        out[COL_DESFECHO_PADRONIZADO] = out[COL_DESFECHO].map(
            standardize_desfecho_upa
        )

    out = apply_group_hierarchy(out, CARDIAC_HIERARCHY)
    out = apply_group_hierarchy(out, METABOLIC_HIERARCHY)

    out[COL_DURACAO_HORAS] = compute_duracao_horas(out)

    return out
