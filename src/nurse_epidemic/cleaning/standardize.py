"""Normalização e limpeza do dataset UPA."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime

import pandas as pd

from nurse_epidemic.schemas.columns import (
    COL_DATA_FIM,
    COL_DATA_INICIO,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
    COL_DURACAO_HORAS,
    COL_FAIXA_ETARIA,
    COL_HORA_FIM,
    COL_HORA_INICIO,
    COL_IDADE_NUMERICA,
    COL_SETOR_DESTINADO,
    COL_SEXO,
    COL_TEMPO_PERMANENCIA,
    YES_NO_COLS,
)

YES_TOKENS = frozenset({"SIM", "S"})
NO_TOKENS = frozenset({"NAO", "NÃO", "N", "NEGA", "NEGOU"})
MAX_LABEL_LEN = 50


def normalize_text(value: object) -> str | None:
    """Normaliza texto: trim, maiúsculas, sem acentos."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().rstrip(".")
    if not text or text == ".":
        return None
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
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

    if COL_TEMPO_PERMANENCIA in out.columns:
        out[COL_TEMPO_PERMANENCIA] = out[COL_TEMPO_PERMANENCIA].map(
            standardize_tempo_permanencia
        )

    if COL_DESFECHO in out.columns:
        out[COL_DESFECHO] = out[COL_DESFECHO].map(normalize_text)
        out[COL_DESFECHO_PADRONIZADO] = out[COL_DESFECHO].map(
            standardize_desfecho_upa
        )

    out[COL_DURACAO_HORAS] = compute_duracao_horas(out)

    return out
