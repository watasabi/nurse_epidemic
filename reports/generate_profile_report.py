#!/usr/bin/env python3
"""Gera relatório HTML autocontido a partir dos CSVs em reports/.

As imagens PNG são embutidas em base64, portanto o arquivo continua
mostrando todos os gráficos mesmo depois de baixado, copiado ou enviado
por e-mail (sem depender da pasta `figures/`).
"""

from __future__ import annotations

import base64
import datetime
import html
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs_version

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DESCRIPTIVE_DIR = REPORTS_DIR / "descriptive"
FIGURES_DIR = REPORTS_DIR / "figures"
PROCESSED_PATH = ROOT / "data" / "processed" / "upa_patients_clean.parquet"

PLOTLY_CDN = f"https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"

ALPHA = 0.05
PREVIEW_ROWS = 20
MAX_BAR_CATEGORIES = 25
DEPARA_PREVIEW_ROWS = 50

COLOR_ACCENT = "#0071e3"
COLOR_MUTED = "#9aa0a6"

CLINICAL_SUMMARY_FILES = {
    "Desfecho clínico": "clin_desfecho.csv",
    "Setor destinado": "clin_setor_destinado.csv",
    "Comorbidades": "clin_comorbidades.csv",
    "Hábitos de vida": "clin_habitos_vida.csv",
    "Tempo de permanência": "clin_tempo_permanencia.csv",
    "Fluxograma (classificação de risco)": "clin_fluxograma.csv",
    "Discriminador (classificação de risco)": "clin_discriminador.csv",
}

FIGURE_CAPTIONS: dict[str, str] = {
    "sexo_bar.png": "Distribuição por sexo",
    "desfecho_bar.png": "Desfecho clínico padronizado",
    "setor_bar.png": "Setor destinado",
    "fluxograma_bar.png": "Fluxogramas mais frequentes (classificação de risco)",
    "discriminador_bar.png": (
        "Discriminadores mais frequentes (classificação de risco)"
    ),
    "association_phik_matrix.png": "Matriz de associação PhiK",
    "association_pvalues.png": (
        "Significância dos testes: cada variável vs. desfecho "
        "padronizado (-log10 do p)"
    ),
}

CSS_CLASSIC = """
body{font-family:Arial,sans-serif;margin:20px;color:#222}
h1,h2{color:#222}
table{border-collapse:collapse;width:100%;margin:8px 0}
th,td{border:1px solid #ddd;padding:6px 8px;text-align:left}
th{background:#f7f7f7}
.section{margin-bottom:28px}
.meta{color:#666;font-size:0.9em}
.warn{background:#fff4e5;border:1px solid #f0c36d;padding:10px;
border-radius:4px}
img{max-width:100%;height:auto;margin:8px 0}
details{margin:8px 0}
.table-wrap{overflow-x:auto}
"""

CSS_MINIMAL = """
:root{--bg:#f5f5f7;--surface:#fff;--text:#1d1d1f;--muted:#6e6e73;
--line:rgba(0,0,0,.08);--accent:#0071e3;--radius:16px}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.page{max-width:920px;margin:0 auto;padding:48px 24px 80px}
.section{background:var(--surface);border:1px solid var(--line);
border-radius:var(--radius);padding:28px;margin-bottom:24px}
h1{font-size:32px;font-weight:600;letter-spacing:-.03em}
h2{font-size:22px;font-weight:600}
.meta{color:var(--muted);font-size:13px}
.warn{background:#fff8e6;border:1px solid #f0c36d;padding:12px 16px;
border-radius:12px;font-size:14px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left}
th{background:#fafafa;color:var(--muted);font-size:12px;
text-transform:uppercase}
.figure-card{border:1px solid var(--line);border-radius:12px;padding:16px;
margin-bottom:16px}
img{width:100%;border-radius:12px;border:1px solid var(--line)}
.toc a{display:inline-block;margin:4px 8px 4px 0;padding:6px 12px;
border-radius:999px;border:1px solid var(--line);
text-decoration:none;color:var(--text)}
.table-wrap{overflow-x:auto}
"""

PERCENT_COLUMNS = ("relativa", "sim_relativa")


def _read_csv(path: Path, index_col: int | None = None) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path, index_col=index_col)


def _format_percent_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Converte proporções (0–1) em percentuais legíveis."""
    work = df.copy()
    for col in work.columns:
        if str(col) in PERCENT_COLUMNS:
            work[col] = pd.to_numeric(work[col], errors="coerce").map(
                lambda v: "—" if pd.isna(v) else f"{100 * v:.1f}%"
            )
    return work


def _df_html(df: pd.DataFrame, *, index: bool = False) -> str:
    table = _format_percent_columns(df).fillna("")
    return (
        '<div class="table-wrap">'
        + table.to_html(index=index, border=0)
        + "</div>"
    )


def _meta(text: str) -> str:
    return f'<p class="meta">{html.escape(text)}</p>'


def _plot_html(fig: go.Figure, height: int = 420) -> str:
    """Serializa figura Plotly sem repetir a biblioteca."""
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        default_height=f"{height}px",
        config={"displaylogo": False, "responsive": True},
    )


def _img_data_uri(path: Path) -> str:
    """Converte PNG em data URI para HTML autocontido."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _is_stale() -> bool:
    """Indica se a base processada é mais recente que os CSVs."""
    if not PROCESSED_PATH.exists() or not DESCRIPTIVE_DIR.exists():
        return False
    csvs = list(DESCRIPTIVE_DIR.glob("*.csv"))
    if not csvs:
        return True
    newest_csv = max(csv.stat().st_mtime for csv in csvs)
    return PROCESSED_PATH.stat().st_mtime > newest_csv


def _stale_banner() -> str:
    if not _is_stale():
        return ""
    return (
        '<div class="section warn">Os CSVs desta pasta são mais antigos '
        "que a base processada. Rode "
        "<code>uv run python reports/export_clinical_summaries.py</code> "
        "antes de publicar este relatório.</div>"
    )


def _phik_heatmap_html() -> str:
    """Heatmap interativo da matriz PhiK."""
    phik = _read_csv(REPORTS_DIR / "association_phik_matrix.csv", index_col=0)
    if phik is None or phik.empty:
        return ""
    labels = [str(c) for c in phik.columns]
    fig = go.Figure(
        go.Heatmap(
            z=phik.to_numpy(),
            x=labels,
            y=[str(i) for i in phik.index],
            zmin=0,
            zmax=1,
            colorscale="Blues",
            text=phik.round(2).to_numpy(),
            texttemplate="%{text}",
            hovertemplate="%{y} × %{x}: %{z:.3f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Matriz PhiK (0 = sem associação, 1 = associação total)",
        margin={"l": 10, "r": 10, "t": 60, "b": 10},
    )
    return _plot_html(fig, height=560)


def _pvalue_chart_html(assoc: pd.DataFrame) -> str:
    """Barras horizontais de -log10(p) por variável."""
    if "p_value" not in assoc.columns or assoc.empty:
        return ""
    work = assoc.copy()
    work["neg_log10_p"] = work["p_value"].apply(_neg_log10)
    work = work.sort_values("neg_log10_p")
    colors = [
        COLOR_ACCENT if p < ALPHA else COLOR_MUTED for p in work["p_value"]
    ]
    fig = go.Figure(
        go.Bar(
            x=work["neg_log10_p"],
            y=work["variable"].astype(str),
            orientation="h",
            marker_color=colors,
            customdata=work[["p_value", "test", "n"]].to_numpy(),
            hovertemplate=(
                "%{y}<br>p = %{customdata[0]:.3g}"
                "<br>teste: %{customdata[1]}"
                "<br>n = %{customdata[2]}<extra></extra>"
            ),
        )
    )
    fig.add_vline(
        x=-math.log10(ALPHA),
        line_dash="dash",
        line_color="#d93025",
        annotation_text="p = 0,05",
    )
    fig.update_layout(
        title="Quanto mais longa a barra, mais forte a evidência",
        xaxis_title="-log10(p)",
        margin={"l": 10, "r": 10, "t": 60, "b": 40},
    )
    return _plot_html(fig, height=460)


def _neg_log10(p_value: float) -> float:
    if pd.isna(p_value) or p_value <= 0:
        return 0.0
    return -math.log10(float(p_value))


def _csv_chart_html(df: pd.DataFrame) -> str:
    """Gráfico de barras para tabelas de frequência."""
    label_col, value_col = _chart_columns(df)
    if label_col is None or value_col is None:
        return ""
    plot_df = df[[label_col, value_col]].dropna()
    if plot_df.empty or len(plot_df) > MAX_BAR_CATEGORIES:
        return ""
    plot_df = plot_df.sort_values(value_col)
    fig = go.Figure(
        go.Bar(
            x=plot_df[value_col],
            y=plot_df[label_col].astype(str),
            orientation="h",
            marker_color=COLOR_ACCENT,
        )
    )
    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 20, "b": 40},
        xaxis_title=str(value_col),
    )
    return _plot_html(fig, height=max(240, 30 * len(plot_df) + 120))


def _chart_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    """Escolhe colunas de rótulo e valor para o gráfico."""
    columns = [str(c) for c in df.columns]
    for value_col in ("absoluta", "sim_absoluta"):
        if value_col in columns:
            label_col = "valor" if "valor" in columns else columns[0]
            if label_col != value_col:
                return label_col, value_col
    return None, None


def _figures_section() -> str:
    """Galeria de PNGs embutidos em base64."""
    parts = [
        '<div class="section" id="figuras"><h2>Figuras</h2>',
        _meta(
            "Imagens embutidas no próprio arquivo: continuam visíveis "
            "mesmo se o HTML for baixado ou enviado sozinho."
        ),
    ]
    pngs = (
        [p for p in sorted(FIGURES_DIR.glob("*.png")) if p.stat().st_size > 0]
        if FIGURES_DIR.exists()
        else []
    )
    if not pngs:
        parts.append("<p>Nenhuma figura disponível.</p></div>")
        return "\n".join(parts)
    for png in pngs:
        cap = FIGURE_CAPTIONS.get(png.name, png.stem.replace("_", " "))
        parts.append('<div class="figure-card">')
        parts.append(f"<h3>{html.escape(cap)}</h3>")
        parts.append(
            f'<img src="{_img_data_uri(png)}" alt="{html.escape(cap)}">'
        )
        parts.append(_meta(f"Arquivo: reports/figures/{png.name}"))
        parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def _association_section() -> str:
    assoc = _read_csv(REPORTS_DIR / "association_results.csv")
    if assoc is None:
        return ""
    parts = [
        '<div class="section" id="associacao"><h2>Associações</h2>',
        _meta(
            f"Fonte: reports/association_results.csv "
            f"({len(assoc)} variáveis testadas) — "
            f"significância adotada: p < {ALPHA}"
        ),
        _phik_heatmap_html(),
        _pvalue_chart_html(assoc),
    ]
    work = assoc.copy()
    if "p_value" in work.columns:
        work["significativa"] = work["p_value"].map(
            lambda p: "sim" if pd.notna(p) and p < ALPHA else "não"
        )
    parts.append("<h3>Resultados dos testes</h3>")
    parts.append(_df_html(work))
    md_path = REPORTS_DIR / "association_results.md"
    if md_path.exists():
        parts.append(
            "<details><summary>Interpretação clínica (texto completo)"
            "</summary><pre>"
            f"{html.escape(md_path.read_text(encoding='utf-8'))}"
            "</pre></details>"
        )
    phik = _read_csv(REPORTS_DIR / "association_phik_matrix.csv", index_col=0)
    if phik is not None:
        parts.append(
            "<details><summary>Matriz PhiK em tabela</summary>"
            + _df_html(phik.round(3), index=True)
            + "</details>"
        )
    parts.append("</div>")
    return "\n".join(p for p in parts if p)


def _correlation_section() -> str:
    corr = _read_csv(REPORTS_DIR / "correlation_results.csv")
    if corr is None:
        return ""
    return "\n".join(
        [
            '<div class="section" id="correlacoes"><h2>Correlações</h2>',
            _meta(
                f"Fonte: reports/correlation_results.csv ({len(corr)} pares)"
            ),
            _df_html(corr),
            "</div>",
        ]
    )


def _clinical_section() -> str:
    parts = [
        '<div class="section" id="clinica">',
        "<h2>Análise descritiva clínica</h2>",
        _meta("Fonte: reports/descriptive/ (tabelas selecionadas)"),
    ]
    for title, fname in CLINICAL_SUMMARY_FILES.items():
        df = _read_csv(DESCRIPTIVE_DIR / fname)
        if df is not None:
            parts.append(f"<h3>{html.escape(title)}</h3>")
            parts.append(_df_html(df))
            parts.append(_meta(f"{fname} — {len(df)} linhas"))
    parts.append("</div>")
    return "\n".join(parts)


def _csv_details_section() -> str:
    if not DESCRIPTIVE_DIR.exists():
        return ""
    parts = [
        '<div class="section" id="descritivos"><h2>CSVs descritivos</h2>',
        _meta("Fonte: reports/descriptive/ (todos os arquivos)"),
    ]
    for csv in sorted(DESCRIPTIVE_DIR.glob("*.csv")):
        df = pd.read_csv(csv)
        parts.append(
            f"<details><summary>{html.escape(csv.name)} "
            f"({len(df)} linhas)</summary>"
        )
        parts.append(_df_html(df.head(PREVIEW_ROWS)))
        parts.append(_csv_chart_html(df))
        described = df.describe(include="all").reset_index()
        parts.append(
            "<details><summary>Estatísticas do arquivo</summary>"
            + _df_html(described)
            + "</details>"
        )
        parts.append("</details>")
    parts.append("</div>")
    return "\n".join(p for p in parts if p)


def _depara_section() -> str:
    col = _read_csv(REPORTS_DIR / "depara_colunas.csv")
    val = _read_csv(REPORTS_DIR / "depara_valores.csv")
    if col is None and val is None:
        return ""
    parts = [
        '<div class="section" id="depara"><h2>De-para de normalizações</h2>',
        "<p>Mapeamento entre dados originais da planilha e valores "
        "padronizados usados nas análises.</p>",
    ]
    if col is not None:
        parts.append("<h3>Colunas</h3>")
        parts.append(_df_html(col))
    if val is not None:
        parts.append("<h3>Valores (amostra)</h3>")
        parts.append(_df_html(val.head(DEPARA_PREVIEW_ROWS)))
        parts.append(
            _meta(
                f"Arquivo completo: reports/depara_valores.csv "
                f"({len(val)} linhas). "
                f"Documentação: docs/depara_normalizacoes.md"
            )
        )
    parts.append("</div>")
    return "\n".join(parts)


def _guides_section() -> str:
    """Links para os guias Markdown didáticos."""
    return """
<div class="section" id="guias">
  <h2>Guias de leitura</h2>
  <p>Documentos em Markdown para quem não é estatístico:</p>
  <ul>
    <li><code>reports/COMO_NAVEGAR.md</code>
      — guia de navegação para a enfermagem (comece por aqui)</li>
    <li><code>reports/README.md</code> — mapa geral dos entregáveis</li>
    <li><code>reports/descriptive/README.md</code> — como ler as tabelas</li>
    <li><code>reports/figures/README.md</code> — lista de gráficos</li>
    <li><code>reports/association_results.md</code>
      — interpretação dos testes</li>
    <li><code>reports/correlation_results.md</code>
      — correlações e IC 95%</li>
    <li><code>docs/depara_normalizacoes.md</code>
      — de-para original → limpo</li>
  </ul>
</div>
"""


def generate_html(theme: str = "classic") -> str:
    """Monta HTML completo para o tema escolhido."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    css = CSS_MINIMAL if theme == "minimal" else CSS_CLASSIC
    wrapper_open = '<div class="page">' if theme == "minimal" else ""
    wrapper_close = "</div>" if theme == "minimal" else ""
    toc = """
    <nav class="toc">
      <a href="#guias">Guias</a>
      <a href="#associacao">Associações</a>
      <a href="#correlacoes">Correlações</a>
      <a href="#clinica">Análise clínica</a>
      <a href="#figuras">Figuras</a>
      <a href="#depara">De-para</a>
      <a href="#descritivos">CSVs</a>
    </nav>
    """
    body = [
        "<!DOCTYPE html><html lang='pt-BR'><head>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Relatório UPA Curitiba</title>",
        f'<script src="{PLOTLY_CDN}" charset="utf-8"></script>',
        f"<style>{css}</style></head><body>",
        wrapper_open,
        "<header><h1>Perfil epidemiológico UPA Curitiba</h1>",
        f'<p class="meta">Gerado em {now} — figuras PNG embutidas no '
        "arquivo; gráficos interativos precisam de internet.</p>",
        toc if theme == "minimal" else "",
        "</header>",
        _stale_banner(),
        _guides_section(),
        _association_section(),
        _correlation_section(),
        _clinical_section(),
        _figures_section(),
        _depara_section(),
        _csv_details_section(),
        wrapper_close,
        "</body></html>",
    ]
    return "\n".join(body)


def main() -> None:
    """Gera relatórios classic e minimal."""
    if _is_stale():
        print(
            "Aviso: CSVs mais antigos que data/processed. "
            "Rode reports/export_clinical_summaries.py para atualizar."
        )
    classic = REPORTS_DIR / "profile_report.html"
    minimal = REPORTS_DIR / "profile_report_minimal.html"
    classic.write_text(generate_html("classic"), encoding="utf-8")
    minimal.write_text(generate_html("minimal"), encoding="utf-8")
    print(f"Relatórios gerados:\n  {classic}\n  {minimal}")


if __name__ == "__main__":
    main()
