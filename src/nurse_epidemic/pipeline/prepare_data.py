"""Pipeline de preparação de dados."""

from pathlib import Path

import pandas as pd

from nurse_epidemic.cleaning.depara import export_depara
from nurse_epidemic.cleaning.standardize import clean_and_standardize
from nurse_epidemic.io.loaders import DEFAULT_EXCEL_PATH, load_upa_excel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INTERIM_PATH = PROJECT_ROOT / "data" / "interim" / "upa_patients_raw.parquet"
PROCESSED_PATH = (
    PROJECT_ROOT / "data" / "processed" / "upa_patients_clean.parquet"
)
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"


def _stringify_objects(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas object mistas para string para parquet."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].astype("string")
    return out


def prepare_data(
    excel_path: Path | str = DEFAULT_EXCEL_PATH,
    interim_path: Path | str = INTERIM_PATH,
    processed_path: Path | str = PROCESSED_PATH,
    *,
    export_mapping: bool = True,
) -> pd.DataFrame:
    """Executa ingestão, limpeza e exporta parquet + de-para.

    Args:
        excel_path: Caminho ao Excel bruto.
        interim_path: Destino do parquet renomeado.
        processed_path: Destino do parquet limpo.
        export_mapping: Se True, gera de-para CSV e Markdown.

    Returns:
        DataFrame processado.
    """
    interim_path = Path(interim_path)
    processed_path = Path(processed_path)
    interim_path.parent.mkdir(parents=True, exist_ok=True)
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    raw = load_upa_excel(excel_path)
    raw = _stringify_objects(raw)
    raw.to_parquet(interim_path, index=False)

    clean = clean_and_standardize(raw)
    clean = _stringify_objects(clean)
    clean.to_parquet(processed_path, index=False)

    if export_mapping:
        export_depara(raw, clean, REPORTS_DIR, DOCS_DIR)

    return clean


if __name__ == "__main__":
    df = prepare_data()
    print(f"Processados {len(df)} pacientes -> {PROCESSED_PATH}")
