#!/usr/bin/env python3
"""Exporta tabelas, figuras e resultados inferenciais."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from nurse_epidemic.pipeline.prepare_data import PROCESSED_PATH, prepare_data
from nurse_epidemic.schemas.columns import (
    ASSOCIATION_PREDICTORS,
    COL_DURACAO_HORAS,
    COL_SEXO,
)

ALPHA = 0.05
from nurse_epidemic.stats.association import (
    phik_association_matrix,
    run_association_battery,
)
from nurse_epidemic.stats.clinical_summaries import (
    comorbidades_table,
    desfecho_table,
    doencas_upa_long,
    habitos_vida_table,
    setor_destinado_table,
    tempo_permanencia_table,
)
from nurse_epidemic.stats.correlation import run_correlation_battery
from nurse_epidemic.stats.descriptive import (
    clinical_report,
    demographic_report,
    export_report,
)

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIVE_DIR = ROOT / "reports" / "descriptive"
FIGURES_DIR = ROOT / "reports" / "figures"
REPORTS_DIR = ROOT / "reports"


@dataclass(frozen=True)
class BarChartSpec:
    """Configuração de gráfico de barras."""

    label_col: str
    value_col: str
    title: str
    filename: str
    horizontal: bool = True


def _load_data() -> pd.DataFrame:
    if not Path(PROCESSED_PATH).exists():
        prepare_data()
    return pd.read_parquet(PROCESSED_PATH)


def export_tables(clean: pd.DataFrame) -> list[Path]:
    """Exporta CSVs agrupados para reports/descriptive/."""
    demo = demographic_report(clean)
    demo_paths = export_report(demo, DESCRIPTIVE_DIR, prefix="demo_")

    clin = clinical_report(clean)
    clin_paths = export_report(clin, DESCRIPTIVE_DIR, prefix="clin_")

    summary_tables = {
        "clin_desfecho": desfecho_table(clean),
        "clin_setor_destinado": setor_destinado_table(clean),
        "clin_comorbidades": comorbidades_table(clean),
        "clin_habitos_vida": habitos_vida_table(clean),
        "clin_tempo_permanencia": tempo_permanencia_table(clean),
    }
    summary_paths = export_report(summary_tables, DESCRIPTIVE_DIR)
    return demo_paths + clin_paths + summary_paths


def _save_bar(df: pd.DataFrame, spec: BarChartSpec) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / spec.filename
    plot_df = df.sort_values(spec.value_col, ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.4 * len(plot_df))))
    if spec.horizontal:
        ax.barh(plot_df[spec.label_col], plot_df[spec.value_col])
    else:
        ax.bar(plot_df[spec.label_col], plot_df[spec.value_col])
    ax.set_title(spec.title)
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def export_figures(clean: pd.DataFrame) -> list[Path]:
    """Gera figuras PNG."""
    paths: list[Path] = []

    sexo = clean[COL_SEXO].value_counts().reset_index()
    sexo.columns = ["sexo", "absoluta"]
    paths.append(
        _save_bar(
            sexo,
            BarChartSpec(
                "sexo",
                "absoluta",
                "Distribuição por sexo",
                "sexo_bar.png",
            ),
        )
    )

    desfecho = desfecho_table(clean)
    paths.append(
        _save_bar(
            desfecho.rename(
                columns={"valor": "desfecho", "absoluta": "absoluta"}
            ),
            BarChartSpec(
                "desfecho",
                "absoluta",
                "Desfecho clínico padronizado",
                "desfecho_bar.png",
            ),
        )
    )

    setor = setor_destinado_table(clean)
    paths.append(
        _save_bar(
            setor.rename(columns={"valor": "setor", "absoluta": "absoluta"}),
            BarChartSpec(
                "setor",
                "absoluta",
                "Setor destinado",
                "setor_bar.png",
            ),
        )
    )

    doencas = doencas_upa_long()
    pivot = doencas.pivot_table(
        index="grupo_doenca",
        columns="periodo_upa",
        values="contagem",
        aggfunc="sum",
        fill_value=0,
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind="bar", ax=ax, width=0.8)
    ax.set_title("Doenças por grupo, mês e UPA")
    ax.set_xlabel("Grupo de doença")
    ax.set_ylabel("Contagem")
    ax.legend(title="Período/UPA", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    doencas_path = FIGURES_DIR / "doencas_upa_trend.png"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(doencas_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    paths.append(doencas_path)

    phik = phik_association_matrix(clean)
    phik.to_csv(REPORTS_DIR / "association_phik_matrix.csv")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(phik, annot=True, fmt=".2f", cmap="Blues", ax=ax)
    ax.set_title("Matriz de associação PhiK")
    fig.tight_layout()
    phik_path = FIGURES_DIR / "association_phik_matrix.png"
    fig.savefig(phik_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    paths.append(phik_path)

    return paths


def export_association(clean: pd.DataFrame) -> Path:
    """Exporta resultados de associação e markdown interpretativo."""
    results = run_association_battery(
        clean,
        predictors=ASSOCIATION_PREDICTORS + [COL_DURACAO_HORAS],
        numeric_predictors=[COL_DURACAO_HORAS],
    )
    out_path = REPORTS_DIR / "association_results.csv"
    results.to_csv(out_path, index=False)

    md_lines = [
        "# Resultados de associação com desfecho clínico",
        "",
        "Nível de significância: 5%. Testes aplicados conforme tipo "
        "de variável (χ²/Fisher ou Mann-Whitney/Kruskal-Wallis).",
        "",
        "| Variável | Teste | Estatística | p-valor | n | Nota |",
        "|----------|-------|-------------|---------|---|------|",
    ]
    for _, row in results.iterrows():
        p = row["p_value"]
        sig = "significativo" if p < ALPHA else "não significativo"
        md_lines.append(
            f"| {row['variable']} | {row['test']} | "
            f"{row['statistic']:.4f} | {p:.4f} | {row['n']} | "
            f"{row.get('note') or sig} |"
        )
    md_lines.extend(["", "## Interpretação", ""])
    sig_rows = results[results["p_value"] < ALPHA]
    if sig_rows.empty:
        md_lines.append(
            "Nenhuma associação estatisticamente significativa "
            "com p < 0,05 foi identificada nesta bateria."
        )
    else:
        for _, row in sig_rows.iterrows():
            md_lines.append(
                f"- **{row['variable']}**: associação significativa "
                f"com {row['target']} (p = {row['p_value']:.4f})."
            )

    md_path = REPORTS_DIR / "association_results.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return out_path


def export_correlation(clean: pd.DataFrame) -> Path:
    """Exporta correlações Pearson/Spearman."""
    results = run_correlation_battery(clean)
    out_path = REPORTS_DIR / "correlation_results.csv"
    results.to_csv(out_path, index=False)
    return out_path


def main() -> None:
    """Executa exportação completa."""
    clean = _load_data()
    export_tables(clean)
    export_figures(clean)
    export_association(clean)
    export_correlation(clean)
    print(f"Exportação concluída para {REPORTS_DIR}")


if __name__ == "__main__":
    main()
