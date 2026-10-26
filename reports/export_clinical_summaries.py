#!/usr/bin/env python3
"""Exporta tabelas, figuras e resultados inferenciais."""

from __future__ import annotations

import math
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib_venn import venn2, venn3

from nurse_epidemic.cleaning.standardize import (
    CARDIAC_HIERARCHY,
    METABOLIC_HIERARCHY,
    GroupHierarchy,
    parse_yes_no,
)
from nurse_epidemic.pipeline.prepare_data import (
    INTERIM_PATH,
    PROCESSED_PATH,
    prepare_data,
)
from nurse_epidemic.schemas.columns import (
    ASSOCIATION_PREDICTORS,
    COL_DESFECHO_PADRONIZADO,
    COL_DIABETICO,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_METABOLICAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_DURACAO_HORAS,
    COL_ETILISTA,
    COL_HIPERTENSO,
    COL_LINHA_EXCEL,
    COL_MES_COLETA,
    COL_NEOPLASIAS,
    COL_SAUDE_MENTAL,
    COL_SEXO,
    COL_TABAGISTA,
    COL_USO_SPAS,
)
from nurse_epidemic.stats.association import (
    phik_association_matrix,
    run_association_battery,
)
from nurse_epidemic.stats.clinical_summaries import (
    comorbidades_table,
    desfecho_table,
    discriminador_table,
    fluxograma_table,
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
from nurse_epidemic.stats.overlaps import (
    hierarchy_inconsistencies,
    multimorbidity_table,
    nested_group_table,
    venn_regions_table,
    venn_subsets,
)

ALPHA = 0.05
P_SCI_NOTATION = 0.0001
CORR_MODERATE = 0.3
CORR_STRONG = 0.5
ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIVE_DIR = ROOT / "reports" / "descriptive"
FIGURES_DIR = ROOT / "reports" / "figures"
REPORTS_DIR = ROOT / "reports"

# Paleta categórica validada (dataviz): azul, laranja, verde-água
SERIES_COLORS = ("#2a78d6", "#eb6834", "#1baf7a")
# Cores semânticas, próximas às marcações feitas na planilha
COLOR_HAS = "#008300"
COLOR_OUTRA_CARDIACA = "#2a78d6"
COLOR_DM = "#6250d6"
COLOR_OUTRA_METABOLICA = "#e87ba4"
INK = "#0b0b0b"
INK_MUTED = "#52514e"
VENN_DPI = 300
VENN_TWO_SETS = 2
# Círculo interno do diagrama aninhado (o externo tem raio 1)
INNER_X = 0.4
INNER_R = 0.57

CARDIAC_LABELS = (
    "Doenças cardíacas",
    "Hipertensão arterial (HAS)",
    "Outra doença cardíaca, sem HAS",
)
METABOLIC_LABELS = (
    "Doenças metabólicas",
    "Diabetes mellitus (DM)",
    "Outra doença metabólica, sem DM",
)
HAS_DM_SETS = {"HAS": COL_HIPERTENSO, "Diabetes": COL_DIABETICO}
COMORBIDITY_SETS = {
    "Doenças cardíacas": COL_DOENCAS_CARDIACAS,
    "Doenças metabólicas": COL_DOENCAS_METABOLICAS,
    "Doenças respiratórias crônicas": COL_DOENCAS_RESPIRATORIAS,
}
HABITS_SETS = {"Tabagista": COL_TABAGISTA, "Etilista": COL_ETILISTA}
HABITS_SPAS_SETS = {
    "Tabagista": COL_TABAGISTA,
    "Etilista": COL_ETILISTA,
    "Uso de SPAs": COL_USO_SPAS,
}
MULTIMORBIDITY_COLS = [
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_METABOLICAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_NEOPLASIAS,
    COL_SAUDE_MENTAL,
]


@dataclass(frozen=True)
class VennSpec:
    """Configuração de diagrama de Venn (2 ou 3 conjuntos)."""

    sets: dict[str, str]
    colors: tuple[str, ...]
    title: str
    filename: str


@dataclass(frozen=True)
class NestedVennSpec:
    """Diagrama de um grupo que contém uma doença específica.

    ``colors`` = (cor do grupo/"outras", cor da doença específica).
    """

    hierarchy: GroupHierarchy
    labels: tuple[str, str, str]
    colors: tuple[str, str]
    title: str
    filename: str


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
        "clin_fluxograma": fluxograma_table(clean),
        "clin_discriminador": discriminador_table(clean),
        "clin_cardiacas_hipertensao": nested_group_table(
            clean, CARDIAC_HIERARCHY, CARDIAC_LABELS
        ),
        "clin_metabolicas_diabetes": nested_group_table(
            clean, METABOLIC_HIERARCHY, METABOLIC_LABELS
        ),
        "clin_venn_has_diabetes": venn_regions_table(clean, HAS_DM_SETS),
        "clin_venn_comorbidades": venn_regions_table(clean, COMORBIDITY_SETS),
        "clin_venn_habitos": venn_regions_table(clean, HABITS_SETS),
        "clin_venn_habitos_spas": venn_regions_table(clean, HABITS_SPAS_SETS),
        "clin_multimorbidade": multimorbidity_table(
            clean, MULTIMORBIDITY_COLS
        ),
    }
    summary_paths = export_report(summary_tables, DESCRIPTIVE_DIR)
    return demo_paths + clin_paths + summary_paths


def export_color_qa() -> Path:
    """Lista linhas em que as cores da planilha contradizem SIM/NAO.

    Lê a base intermediária (antes da regra "todo hipertenso é
    cardíaco"), para mostrar o que está de fato na planilha.
    """
    raw = pd.read_parquet(INTERIM_PATH)
    yes_no_cols = [
        COL_HIPERTENSO,
        COL_DOENCAS_CARDIACAS,
        COL_DIABETICO,
        COL_DOENCAS_METABOLICAS,
    ]
    for col in yes_no_cols:
        raw[col] = raw[col].map(parse_yes_no)
    # Só aba + linha do Excel: o repositório é público, então nada de
    # dados clínicos por paciente (sexo, idade, CID) neste arquivo
    qa = pd.concat(
        [
            hierarchy_inconsistencies(raw, CARDIAC_HIERARCHY),
            hierarchy_inconsistencies(raw, METABOLIC_HIERARCHY),
        ],
        ignore_index=True,
    )
    path = DESCRIPTIVE_DIR / "qa_inconsistencias_cores.csv"
    qa.to_csv(path, index=False)
    return path


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


def _pct(value: float) -> str:
    """Porcentagem com vírgula decimal (padrão ABNT)."""
    return f"{value:.1%}".replace(".", ",")


def _save_venn(df: pd.DataFrame, spec: VennSpec) -> Path:
    """Desenha um Venn com contagem e % por região exclusiva."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / spec.filename
    labels = list(spec.sets)
    subsets = venn_subsets(df, list(spec.sets.values()))
    n_valid = sum(subsets.values())
    none_key = "0" * len(labels)
    regions = {k: v for k, v in subsets.items() if k != none_key}
    totals = [
        sum(v for k, v in regions.items() if k[i] == "1")
        for i in range(len(labels))
    ]
    set_labels = [
        f"{lab}\nn = {tot} ({_pct(tot / n_valid)})"
        for lab, tot in zip(labels, totals)
    ]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    draw = venn2 if len(labels) == VENN_TWO_SETS else venn3
    diagram = draw(
        subsets=regions,
        set_labels=set_labels,
        set_colors=spec.colors,
        alpha=0.55,
        ax=ax,
    )
    for key, count in regions.items():
        patch = diagram.get_patch_by_id(key)
        if patch is not None:
            patch.set_edgecolor("white")
            patch.set_linewidth(2)
        text = diagram.get_label_by_id(key)
        if text is None:
            continue
        if count == 0:
            text.set_text("")
            continue
        text.set_text(f"{count}\n({_pct(count / n_valid)})")
        text.set_fontsize(10)
        text.set_color(INK)
    for text in diagram.set_labels:
        if text is not None:
            text.set_fontsize(11)
            text.set_fontweight("bold")
            text.set_color(INK)

    ax.set_title(spec.title, fontsize=13, color=INK, pad=14)
    fig.text(
        0.5,
        0.02,
        f"Pacientes com informação: n = {n_valid}. "
        f"Sem nenhuma das condições: {subsets[none_key]} "
        f"({_pct(subsets[none_key] / n_valid)}).",
        ha="center",
        fontsize=9,
        color=INK_MUTED,
    )
    fig.savefig(path, dpi=VENN_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


VENN_SPECS = [
    VennSpec(
        sets=HAS_DM_SETS,
        colors=(COLOR_HAS, COLOR_DM),
        title="Hipertensão e diabetes",
        filename="venn_has_diabetes.png",
    ),
    VennSpec(
        sets=COMORBIDITY_SETS,
        colors=SERIES_COLORS,
        title="Sobreposição entre grupos de comorbidades",
        filename="venn_comorbidades.png",
    ),
    VennSpec(
        sets=HABITS_SETS,
        colors=SERIES_COLORS[:2],
        title="Tabagismo e etilismo",
        filename="venn_habitos.png",
    ),
    VennSpec(
        sets=HABITS_SPAS_SETS,
        colors=SERIES_COLORS,
        title="Tabagismo, etilismo e uso de SPAs",
        filename="venn_habitos_spas.png",
    ),
]


NESTED_VENN_SPECS = [
    NestedVennSpec(
        hierarchy=CARDIAC_HIERARCHY,
        labels=CARDIAC_LABELS,
        colors=(COLOR_OUTRA_CARDIACA, COLOR_HAS),
        title="Hipertensão dentro das doenças cardíacas",
        filename="venn_cardiacas_hipertensao.png",
    ),
    NestedVennSpec(
        hierarchy=METABOLIC_HIERARCHY,
        labels=METABOLIC_LABELS,
        colors=(COLOR_OUTRA_METABOLICA, COLOR_DM),
        title="Diabetes dentro das doenças metabólicas",
        filename="venn_metabolicas_diabetes.png",
    ),
]


def _save_nested_venn(df: pd.DataFrame, spec: NestedVennSpec) -> Path:
    """Desenha um círculo (doença específica) dentro do grupo.

    Esquemático: as áreas não são proporcionais, pois a doença
    específica ocupa quase todo o grupo e o anel das "outras" ficaria
    fino demais para ler.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / spec.filename
    table = nested_group_table(df, spec.hierarchy, spec.labels)
    counts = dict(zip(table["categoria"], table["absoluta"]))
    pcts = dict(zip(table["categoria"], table["relativa"]))
    group_label, specific_label, other_label = spec.labels
    group_key = f"{group_label} (total)"
    n_valid = int(table["n_valido"].iloc[0])
    outer_color, inner_color = spec.colors

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.add_patch(
        plt.Circle(
            (0, 0),
            1.0,
            facecolor=outer_color,
            alpha=0.45,
            edgecolor="white",
            linewidth=2,
        )
    )
    ax.add_patch(
        plt.Circle(
            (INNER_X, 0),
            INNER_R,
            facecolor=inner_color,
            alpha=0.6,
            edgecolor="white",
            linewidth=2,
        )
    )
    ax.text(
        INNER_X,
        0,
        f"{textwrap.fill(specific_label, 14)}\n{counts[specific_label]} "
        f"({_pct(pcts[specific_label])})",
        ha="center",
        va="center",
        fontsize=11,
        color=INK,
    )
    ax.text(
        (INNER_X - INNER_R - 1) / 2,
        0,
        f"{textwrap.fill(other_label, 12)}\n"
        f"{counts[other_label]} ({_pct(pcts[other_label])})",
        ha="center",
        va="center",
        fontsize=10,
        color=INK,
    )
    ax.text(
        0,
        1.08,
        f"{group_label}: n = {counts[group_key]} ({_pct(pcts[group_key])})",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        color=INK,
    )
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.05, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(spec.title, fontsize=13, color=INK, pad=4)
    fig.text(
        0.5,
        0.01,
        f"Pacientes com informação: n = {n_valid}. Esquema sem áreas "
        "proporcionais.\nQuem tem "
        f"{specific_label.split(' (')[0].lower()} pode ter também "
        "outra doença do grupo (a planilha não distingue).",
        ha="center",
        fontsize=9,
        color=INK_MUTED,
    )
    fig.savefig(path, dpi=VENN_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def export_venns(clean: pd.DataFrame) -> list[Path]:
    """Gera os diagramas de Venn (PNG 300 dpi, para o trabalho)."""
    nested = [_save_nested_venn(clean, spec) for spec in NESTED_VENN_SPECS]
    return nested + [_save_venn(clean, spec) for spec in VENN_SPECS]


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

    TOP_N_CATEGORIES = 15

    fluxograma = fluxograma_table(clean).nlargest(TOP_N_CATEGORIES, "absoluta")
    paths.append(
        _save_bar(
            fluxograma.rename(columns={"valor": "fluxograma"}),
            BarChartSpec(
                "fluxograma",
                "absoluta",
                "Fluxogramas mais frequentes na classificação de risco",
                "fluxograma_bar.png",
            ),
        )
    )

    discriminador = discriminador_table(clean).nlargest(
        TOP_N_CATEGORIES, "absoluta"
    )
    paths.append(
        _save_bar(
            discriminador.rename(columns={"valor": "discriminador"}),
            BarChartSpec(
                "discriminador",
                "absoluta",
                "Discriminadores mais frequentes na classificação de risco",
                "discriminador_bar.png",
            ),
        )
    )

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


def _save_pvalue_chart(results: pd.DataFrame) -> Path:
    """Gera figura estática de -log10(p) por variável."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "association_pvalues.png"
    plot_df = results.copy()
    plot_df["neg_log10_p"] = plot_df["p_value"].apply(
        lambda p: -math.log10(p) if pd.notna(p) and p > 0 else 0.0
    )
    plot_df = plot_df.sort_values("neg_log10_p")
    colors = [
        "#0071e3" if p < ALPHA else "#9aa0a6" for p in plot_df["p_value"]
    ]
    target = (
        str(plot_df["target"].iloc[0])
        if not plot_df.empty
        else COL_DESFECHO_PADRONIZADO
    )
    fig, ax = plt.subplots(figsize=(10, max(4, 0.5 * len(plot_df))))
    ax.barh(plot_df["variable"], plot_df["neg_log10_p"], color=colors)
    ax.axvline(-math.log10(ALPHA), color="#d93025", linestyle="--")
    ax.set_xlabel("-log10(p)")
    ax.set_ylabel(f"Variável testada (cada uma vs. {target})")
    ax.set_title(
        "Significância dos testes: cada variável vs. "
        f"{target}\n(barra maior = evidência maior)"
    )
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


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
    _save_pvalue_chart(results)
    return out_path


def export_correlation(clean: pd.DataFrame) -> Path:
    """Exporta correlações Pearson/Spearman e guia Markdown."""
    results = run_correlation_battery(clean)
    out_path = REPORTS_DIR / "correlation_results.csv"
    results.to_csv(out_path, index=False)
    _write_correlation_markdown(results)
    return out_path


def _md_table(df: pd.DataFrame, label_col: str, base: str) -> list[str]:
    """Tabela Markdown com n e % (vírgula decimal) por linha."""
    lines = [f"| {base} | n | % |", "|---|---:|---:|"]
    for _, row in df.iterrows():
        lines.append(
            f"| {row[label_col]} | {int(row['absoluta'])} | "
            f"{_pct(row['relativa'])} |"
        )
    return lines


def _share(part: int, whole: int) -> str:
    """ "x de y (z%)" para frases de interpretação."""
    return f"{part} de {whole} ({_pct(part / whole if whole else 0.0)})"


def _nested_md(
    clean: pd.DataFrame,
    spec: NestedVennSpec,
    heading: str,
    adjective: str,
) -> list[str]:
    """Seção Markdown de um grupo com doença específica + outras."""
    table = nested_group_table(clean, spec.hierarchy, spec.labels)
    counts = dict(zip(table["categoria"], table["absoluta"]))
    group_label, specific_label, other_label = spec.labels
    total = counts[f"{group_label} (total)"]
    return [
        f"## {heading}",
        "",
        *_md_table(table, "categoria", "Categoria"),
        "",
        f"Das {total} pessoas com {group_label.lower()}, "
        f"{counts[specific_label]} ({_pct(counts[specific_label] / total)}) "
        f"são {adjective} e {counts[other_label]} "
        f"({_pct(counts[other_label] / total)}) têm "
        f"{other_label[0].lower()}{other_label[1:]}.",
        "",
        f"Figura: `figures/{spec.filename}` (esquema sem áreas "
        "proporcionais).",
        "",
    ]


def _pair_md(
    clean: pd.DataFrame,
    spec: VennSpec,
    heading: str,
    plurals: tuple[str, str],
) -> list[str]:
    """Seção Markdown de um Venn de 2 conjuntos, com frase-resumo."""
    sub = venn_subsets(clean, list(spec.sets.values()))
    n_a = sub["10"] + sub["11"]
    n_b = sub["01"] + sub["11"]
    return [
        f"## {heading}",
        "",
        *_md_table(
            venn_regions_table(clean, spec.sets), "combinacao", "Grupo"
        ),
        "",
        f"Entre os {plurals[0]}, {_share(sub['11'], n_a)} também são "
        f"{plurals[1]}; entre os {plurals[1]}, "
        f"{_share(sub['11'], n_b)} também são {plurals[0]}.",
        "",
        f"Figura: `figures/{spec.filename}`.",
        "",
    ]


def _regions_md(
    clean: pd.DataFrame, spec: VennSpec, heading: str, intro: str
) -> list[str]:
    """Seção Markdown de um Venn de 3 conjuntos."""
    return [
        f"## {heading}",
        "",
        intro,
        "",
        *_md_table(
            venn_regions_table(clean, spec.sets), "combinacao", "Combinação"
        ),
        "",
        f"Figura: `figures/{spec.filename}`.",
        "",
    ]


def _multimorbidity_md(clean: pd.DataFrame) -> list[str]:
    """Seção Markdown de multimorbidade."""
    multi = multimorbidity_table(clean, MULTIMORBIDITY_COLS)
    n_multi = int(multi.loc[multi["n_grupos"] >= 2, "absoluta"].sum())  # noqa: PLR2004
    return [
        "## 5. Multimorbidade",
        "",
        "Quantos grupos de comorbidade cada paciente acumula "
        "(cardíacas, metabólicas, respiratórias crônicas, neoplasias e "
        "saúde mental).",
        "",
        *_md_table(
            multi.assign(n_grupos=multi["n_grupos"].astype(str)),
            "n_grupos",
            "Nº de grupos",
        ),
        "",
        f"{_share(n_multi, int(multi['n_valido'].iloc[0]))} pacientes "
        "têm dois ou mais grupos de comorbidade.",
        "",
    ]


def _qa_md(qa: pd.DataFrame) -> list[str]:
    """Seção Markdown com linhas da planilha a revisar."""
    lines = ["## Pontos para revisar na planilha", ""]
    if qa.empty:
        return [*lines, "Nenhuma inconsistência entre cores e SIM/NÃO.", ""]
    lines.extend(
        [
            "Linhas em que a cor contradiz as colunas SIM/NÃO (lista "
            "completa em `descriptive/qa_inconsistencias_cores.csv`):",
            "",
        ]
    )
    lines.extend(
        f"- Aba {row[COL_MES_COLETA]}, linha "
        f"{int(row[COL_LINHA_EXCEL])}: {row['problema']}."
        for _, row in qa.iterrows()
    )
    lines.extend(
        [
            "",
            "Enquanto não forem corrigidas, vale a regra acima: "
            "hipertensão vem da coluna *Hipertenso* e 'outra cardíaca' "
            "vem da célula azul (idem para diabetes/rosa).",
            "",
        ]
    )
    return lines


def _write_overlap_markdown(clean: pd.DataFrame, qa: pd.DataFrame) -> Path:
    """Gera guia de leitura das sobreposições (Venn) para o trabalho."""
    venns = {spec.filename: spec for spec in VENN_SPECS}
    cardiac_spec, metabolic_spec = NESTED_VENN_SPECS
    md = [
        "# Comorbidades e hábitos de vida: sobreposições (Venn)",
        "",
        "Um mesmo paciente pode ter mais de uma comorbidade ou hábito. "
        "Por isso as porcentagens de cada condição, somadas, passam de "
        "100%. Os diagramas de Venn e as tabelas abaixo contam **cada "
        "paciente uma única vez**, na região que corresponde à sua "
        "combinação de condições.",
        "",
        "- Tabelas: `descriptive/clin_cardiacas_hipertensao.csv`, "
        "`clin_metabolicas_diabetes.csv`, `clin_venn_*.csv` e "
        "`clin_multimorbidade.csv`",
        "- Figuras (PNG 300 dpi, prontas para o trabalho): "
        "`figures/venn_*.png`",
        "- Percentuais sobre os pacientes com informação (`n_valido`). "
        "Um paciente sem registro de comorbidades/hábitos fica fora "
        "das análises que usam essas colunas; por isso alguns n são "
        "327 e outros 328.",
        "",
        "## Como a planilha foi lida (marcação por cores)",
        "",
        "| Coluna da planilha | Cor | Significado |",
        "|---|---|---|",
        "| DOENÇAS CARDÍACAS | verde | tem hipertensão (HAS) |",
        "| DOENÇAS CARDÍACAS | azul | outra doença cardíaca, **sem** HAS |",
        "| DOENÇAS METABÓLICAS | roxo | tem diabetes (DM) |",
        "| DOENÇAS METABÓLICAS | rosa | outra doença metabólica, **sem** DM |",
        "",
        "- Regra aplicada: todo hipertenso conta em doenças cardíacas e "
        "todo diabético em doenças metabólicas.",
        "- **Limitação:** verde/roxo não exclui outra doença do mesmo "
        "grupo. Não dá para saber quantos hipertensos têm também outra "
        "doença cardíaca (idem para diabetes). Vale citar isso no texto.",
        "",
        *_nested_md(
            clean,
            cardiac_spec,
            "1. Doenças cardíacas: hipertensão × outras",
            "hipertensas",
        ),
        *_nested_md(
            clean,
            metabolic_spec,
            "2. Doenças metabólicas: diabetes × outras",
            "diabéticas",
        ),
        *_pair_md(
            clean,
            venns["venn_has_diabetes.png"],
            "3. Hipertensão e diabetes",
            ("hipertensos", "diabéticos"),
        ),
        *_regions_md(
            clean,
            venns["venn_comorbidades.png"],
            "4. Grupos de comorbidades",
            "Doenças cardíacas (inclui HAS), metabólicas (inclui DM) e "
            "respiratórias crônicas.",
        ),
        *_multimorbidity_md(clean),
        *_pair_md(
            clean,
            venns["venn_habitos.png"],
            "6. Hábitos de vida: tabagismo e etilismo",
            ("tabagistas", "etilistas"),
        ),
        *_regions_md(
            clean,
            venns["venn_habitos_spas.png"],
            "7. Tabagismo, etilismo e uso de SPAs",
            "SPAs = substâncias psicoativas.",
        ),
        "## Como ler um diagrama de Venn",
        "",
        "- Cada círculo é uma condição; o número junto do nome é o "
        "total de pacientes com ela.",
        "- Os números **dentro** das regiões são exclusivos: quem está "
        "na interseção não é contado de novo nas outras partes.",
        "- Nos diagramas de 2 e 3 círculos, o tamanho é aproximadamente "
        "proporcional ao número de pacientes. Nos de hipertensão e "
        "diabetes dentro do grupo, o desenho é só esquemático.",
        "",
        *_qa_md(qa),
        "## Regenerar",
        "",
        "```bash",
        "uv run python -m nurse_epidemic.pipeline.prepare_data",
        "uv run python reports/export_clinical_summaries.py",
        "uv run python reports/generate_profile_report.py",
        "```",
        "",
    ]
    path = REPORTS_DIR / "comorbidades_habitos_venn.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path


def main() -> None:
    """Executa exportação completa."""
    clean = _load_data()
    export_tables(clean)
    qa = pd.read_csv(export_color_qa())
    export_figures(clean)
    export_venns(clean)
    _write_overlap_markdown(clean, qa)
    export_association(clean)
    export_correlation(clean)
    print(f"Exportação concluída para {REPORTS_DIR}")


if __name__ == "__main__":
    main()
