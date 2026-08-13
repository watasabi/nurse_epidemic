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
    COL_DESFECHO_PADRONIZADO,
    COL_DURACAO_HORAS,
    COL_SEXO,
)
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

ALPHA = 0.05
P_SCI_NOTATION = 0.0001
CORR_MODERATE = 0.3
CORR_STRONG = 0.5
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


def _test_label(test_name: str) -> str:
    """Nome amigável do teste estatístico."""
    mapping = {
        "chi2": "χ² (qui-quadrado)",
        "fisher_exact": "Fisher exato",
        "kruskal": "Kruskal-Wallis",
        "mannwhitneyu": "Mann-Whitney",
        "none": "não aplicado",
    }
    return mapping.get(str(test_name), str(test_name))


def _fmt_p(p: float) -> str:
    """Formata p-valor para leitura humana."""
    if pd.isna(p):
        return "—"
    if p < P_SCI_NOTATION:
        return f"{p:.2e}"
    return f"{p:.4f}"


def _write_association_markdown(
    results: pd.DataFrame,
    n_patients: int,
) -> Path:
    """Gera guia interpretativo de associações (público leigo)."""
    target = (
        str(results["target"].iloc[0])
        if not results.empty
        else COL_DESFECHO_PADRONIZADO
    )
    sig_rows = results[results["p_value"] < ALPHA]
    md_lines = [
        "# Associação entre variáveis clínicas e desfecho",
        "",
        "Este relatório explica, em linguagem simples, os testes usados "
        "para avaliar se características clínicas estão associadas ao "
        "desfecho do atendimento na UPA.",
        "",
        "- Arquivo numérico: `reports/association_results.csv`",
        f"- Pacientes analisados (máx.): **{n_patients}**",
        f"- Variável alvo: `{target}` "
        "(ALTA, INTERNAMENTO, ENCAMINHAMENTO, OBITO)",
        f"- Nível de significância: **{ALPHA:.0%}** (p < {ALPHA})",
        "",
        "## O que testamos?",
        "",
        "Cada linha da tabela é uma variável clínica cruzada com o "
        "desfecho padronizado.",
        "",
        "- Variáveis **categóricas** (SIM/NAO, setor, tempo): teste "
        "**χ²**; se a tabela for 2×2 com alguma célula < 5, usa-se "
        "**Fisher exato**.",
        "- Variável **numérica** `duracao_horas`: "
        "**Kruskal-Wallis** (ou Mann-Whitney se houver só 2 grupos), "
        "comparando a distribuição da duração entre os desfechos.",
        "",
        "### Por que esses testes?",
        "",
        "- **χ² / Fisher**: a proporção de desfechos é diferente entre "
        "grupos? Ex.: tabagistas vs não tabagistas.",
        "- **Kruskal-Wallis**: a duração do atendimento difere entre "
        "os grupos de desfecho, sem exigir normalidade dos dados.",
        "",
        "## Como entender o valor-p",
        "",
        "O p-valor é a probabilidade de vermos um resultado tão "
        "(ou mais) extremo **se não houvesse associação real**.",
        "",
        f"- Se p < {ALPHA}: associação **estatisticamente significativa**.",
        f"- Se p ≥ {ALPHA}: **não há evidência suficiente** de associação "
        "neste conjunto de dados.",
        "",
        "### Hipótese nula",
        "",
        "Para todos os testes: **não existe associação** entre a "
        "variável e o desfecho. Rejeitar a hipótese nula = há associação "
        "estatística (não implica, sozinha, causalidade clínica).",
        "",
        "## Resultados principais",
        "",
    ]
    if sig_rows.empty:
        md_lines.append(
            "Nenhuma associação com p < 0,05 foi identificada nesta bateria."
        )
    else:
        md_lines.append(
            "Variáveis com associação estatisticamente significativa:"
        )
        md_lines.append("")
        for _, row in sig_rows.iterrows():
            md_lines.append(
                f"- `{row['variable']}` — {_test_label(row['test'])}: "
                f"p ≈ {_fmt_p(row['p_value'])} (n = {int(row['n'])})."
            )
    md_lines.extend(
        [
            "",
            "## Tabela completa dos testes",
            "",
            "| Variável | Tipo de teste | p-value | n | Associação? |",
            "|---|---|---|---|---|",
        ]
    )
    for _, row in results.iterrows():
        p = row["p_value"]
        assoc = "significativa" if p < ALPHA else "não significativa"
        md_lines.append(
            f"| {row['variable']} | {_test_label(row['test'])} | "
            f"{_fmt_p(p)} | {int(row['n'])} | {assoc} |"
        )
    md_lines.extend(
        [
            "",
            "## Matriz PhiK",
            "",
            "Além dos p-valores, geramos uma matriz PhiK "
            "(`association_phik_matrix.csv` e figura "
            "`figures/association_phik_matrix.png`).",
            "",
            "- Escala de **0 a 1** (quanto maior, mais associação).",
            "- Útil como visão geral entre várias variáveis ao mesmo tempo.",
            "",
            "## Como usar este relatório",
            "",
            "1. Leia os resultados principais acima.",
            "2. Confira números em `association_results.csv`.",
            "3. Compare com os gráficos em `figures/` e as tabelas em "
            "`descriptive/`.",
            "4. Para saber como os valores brutos foram padronizados, "
            "veja `../docs/depara_normalizacoes.md`.",
            "",
            "## Gerar o HTML interativo",
            "",
            "```bash",
            "uv run python reports/generate_profile_report.py",
            "```",
            "",
            "Isso atualiza `profile_report.html` e "
            "`profile_report_minimal.html`.",
            "",
        ]
    )
    md_path = REPORTS_DIR / "association_results.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path


def _write_correlation_markdown(results: pd.DataFrame) -> Path:
    """Gera guia interpretativo de correlações."""
    md_lines = [
        "# Correlações entre variáveis numéricas",
        "",
        "Este relatório explica as correlações calculadas na Fase 2 "
        "(Pearson ou Spearman, com intervalo de confiança de 95%).",
        "",
        "- Arquivo numérico: `reports/correlation_results.csv`",
        f"- Nível de significância: **{ALPHA:.0%}**",
        "",
        "## O que é correlação?",
        "",
        "Correlação mede se duas variáveis numéricas **andam juntas**:",
        "",
        "- **r próximo de +1**: quando uma sobe, a outra tende a subir.",
        "- **r próximo de −1**: quando uma sobe, a outra tende a cair.",
        "- **r próximo de 0**: pouco relacionamento linear/monotônico.",
        "",
        "Correlação **não prova causa**; só descreve associação numérica.",
        "",
        "## Pearson ou Spearman?",
        "",
        "- **Pearson**: adequado quando as duas variáveis se aproximam "
        "de uma distribuição normal.",
        "- **Spearman**: usa postos (ranks); preferido quando a "
        "normalidade falha (padrão clínico frequente).",
        "",
        "O pipeline testa normalidade (Shapiro) e escolhe o método.",
        "",
        "## Intervalo de confiança (IC 95%)",
        "",
        "O IC 95% é uma faixa plausível para o verdadeiro r na "
        "população. Se o intervalo **cruza o zero**, a correlação "
        "costuma ser compatível com “sem associação”.",
        "",
        "## Resultados",
        "",
        "| Variável A | Variável B | Método | r | IC 95% | p-value | n |",
        "|---|---|---|---|---|---|---|",
    ]
    if results.empty:
        md_lines.append("| — | — | — | — | — | — | — |")
    else:
        for _, row in results.iterrows():
            lo = row.get("ci_lower")
            hi = row.get("ci_upper")
            ci = (
                f"[{lo:.3f}, {hi:.3f}]"
                if pd.notna(lo) and pd.notna(hi)
                else "—"
            )
            r = row["r"]
            r_txt = f"{r:.4f}" if pd.notna(r) else "—"
            md_lines.append(
                f"| {row['variable_a']} | {row['variable_b']} | "
                f"{row['method']} | {r_txt} | {ci} | "
                f"{_fmt_p(row['p_value'])} | {int(row['n'])} |"
            )
    md_lines.extend(
        [
            "",
            "## Interpretação prática",
            "",
        ]
    )
    if results.empty:
        md_lines.append("Nenhum par numérico disponível nesta execução.")
    else:
        for _, row in results.iterrows():
            p = row["p_value"]
            r = row["r"]
            strength = "fraca"
            if pd.notna(r) and abs(r) >= CORR_STRONG:
                strength = "moderada a forte"
            elif pd.notna(r) and abs(r) >= CORR_MODERATE:
                strength = "moderada"
            sig = (
                "estatisticamente significativa"
                if pd.notna(p) and p < ALPHA
                else "não significativa (p ≥ 0,05)"
            )
            r_disp = f"{r:.3f}" if pd.notna(r) else "—"
            md_lines.append(
                f"- `{row['variable_a']}` × `{row['variable_b']}`: "
                f"correlação {strength} (r ≈ {r_disp}), {sig}."
            )
    md_lines.extend(
        [
            "",
            "## Como usar",
            "",
            "1. Use esta página para o texto de resultados/discussão.",
            "2. Detalhes em `correlation_results.csv`.",
            "3. Para associação categórica × desfecho, veja "
            "`association_results.md`.",
            "",
        ]
    )
    md_path = REPORTS_DIR / "correlation_results.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path


def export_association(clean: pd.DataFrame) -> Path:
    """Exporta resultados de associação e markdown interpretativo."""
    results = run_association_battery(
        clean,
        predictors=ASSOCIATION_PREDICTORS + [COL_DURACAO_HORAS],
        numeric_predictors=[COL_DURACAO_HORAS],
    )
    out_path = REPORTS_DIR / "association_results.csv"
    results.to_csv(out_path, index=False)
    _write_association_markdown(results, n_patients=len(clean))
    return out_path


def export_correlation(clean: pd.DataFrame) -> Path:
    """Exporta correlações Pearson/Spearman e guia Markdown."""
    results = run_correlation_battery(clean)
    out_path = REPORTS_DIR / "correlation_results.csv"
    results.to_csv(out_path, index=False)
    _write_correlation_markdown(results)
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
