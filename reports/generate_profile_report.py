#!/usr/bin/env python3
"""Gera relatório HTML a partir dos CSVs em reports/."""

from __future__ import annotations

import datetime
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DESCRIPTIVE_DIR = REPORTS_DIR / "descriptive"
FIGURES_DIR = REPORTS_DIR / "figures"

CLINICAL_SUMMARY_FILES = {
    "Desfecho clínico": "clin_desfecho.csv",
    "Setor destinado": "clin_setor_destinado.csv",
    "Comorbidades": "clin_comorbidades.csv",
    "Hábitos de vida": "clin_habitos_vida.csv",
    "Tempo de permanência": "clin_tempo_permanencia.csv",
}

FIGURE_CAPTIONS: dict[str, str] = {
    "sexo_bar.png": "Distribuição por sexo",
    "desfecho_bar.png": "Desfecho clínico padronizado",
    "setor_bar.png": "Setor destinado",
    "doencas_upa_trend.png": "Doenças por grupo, mês e UPA",
    "association_phik_matrix.png": "Matriz de associação PhiK",
}

CSS_CLASSIC = """
body{font-family:Arial,sans-serif;margin:20px;color:#222}
h1,h2{color:#222}
table{border-collapse:collapse;width:100%;margin:8px 0}
th,td{border:1px solid #ddd;padding:6px 8px;text-align:left}
th{background:#f7f7f7}
.section{margin-bottom:28px}
.meta{color:#666;font-size:0.9em}
img{max-width:100%;height:auto;margin:8px 0}
details{margin:8px 0}
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
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left}
th{background:#fafafa;color:var(--muted);font-size:12px;text-transform:uppercase}
img{width:100%;border-radius:12px;border:1px solid var(--line)}
.toc a{display:inline-block;margin:4px 8px 4px 0;padding:6px 12px;
border-radius:999px;border:1px solid var(--line);
text-decoration:none;color:var(--text)}
"""


def _read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def _df_html(df: pd.DataFrame) -> str:
    return df.fillna("").to_html(index=False, border=0)


def _figures_section() -> str:
    if not FIGURES_DIR.exists():
        return "<p>Nenhuma figura disponível.</p>"
    parts = ['<div class="section" id="figuras"><h2>Figuras</h2>']
    for png in sorted(FIGURES_DIR.glob("*.png")):
        cap = FIGURE_CAPTIONS.get(png.name, png.stem.replace("_", " "))
        parts.append(f"<h3>{cap}</h3>")
        parts.append(f'<img src="figures/{png.name}" alt="{cap}">')
    parts.append("</div>")
    return "\n".join(parts)


def _association_section() -> str:
    assoc = _read_csv(REPORTS_DIR / "association_results.csv")
    if assoc is None:
        return ""
    parts = ['<div class="section" id="associacoes"><h2>Associações</h2>']
    if "p_value" in assoc.columns:
        work = assoc.copy()
        work["neg_log10_p"] = work["p_value"].apply(
            lambda p: -math.log10(p) if p > 0 else 0.0
        )
        parts.append(_df_html(work))
    md_path = REPORTS_DIR / "association_results.md"
    if md_path.exists():
        parts.append(
            f"<details><summary>Interpretação clínica</summary>"
            f"<pre>{md_path.read_text(encoding='utf-8')}</pre></details>"
        )
    phik = _read_csv(REPORTS_DIR / "association_phik_matrix.csv")
    if phik is not None:
        parts.append("<h3>Matriz PhiK</h3>")
        parts.append(_df_html(phik))
    parts.append("</div>")
    return "\n".join(parts)


def _correlation_section() -> str:
    corr = _read_csv(REPORTS_DIR / "correlation_results.csv")
    if corr is None:
        return ""
    return (
        '<div class="section" id="correlacoes"><h2>Correlações</h2>'
        + _df_html(corr)
        + "</div>"
    )


def _clinical_section() -> str:
    parts = [
        '<div class="section" id="descritiva">',
        "<h2>Análise descritiva clínica</h2>",
    ]
    for title, fname in CLINICAL_SUMMARY_FILES.items():
        df = _read_csv(DESCRIPTIVE_DIR / fname)
        if df is not None:
            parts.append(f"<h3>{title}</h3>")
            parts.append(_df_html(df))
    parts.append("</div>")
    return "\n".join(parts)


def _csv_details_section() -> str:
    if not DESCRIPTIVE_DIR.exists():
        return ""
    parts = ['<div class="section" id="csvs"><h2>CSVs descritivos</h2>']
    for csv in sorted(DESCRIPTIVE_DIR.glob("*.csv")):
        df = pd.read_csv(csv)
        parts.append(f"<details><summary>{csv.name}</summary>")
        parts.append(_df_html(df.head(20)))
        parts.append("</details>")
    parts.append("</div>")
    return "\n".join(parts)


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
        parts.append(_df_html(val.head(50)))
        parts.append(
            f'<p class="meta">Arquivo completo: reports/depara_valores.csv '
            f"({len(val)} linhas). "
            f"Documentação: docs/depara_normalizacoes.md</p>"
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
    """Monta HTML completo."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    css = CSS_MINIMAL if theme == "minimal" else CSS_CLASSIC
    wrapper_open = '<div class="page">' if theme == "minimal" else ""
    wrapper_close = "</div>" if theme == "minimal" else ""
    toc = """
    <nav class="toc">
      <a href="#guias">Guias</a>
      <a href="#associacoes">Associações</a>
      <a href="#correlacoes">Correlações</a>
      <a href="#descritiva">Descritiva</a>
      <a href="#figuras">Figuras</a>
      <a href="#depara">De-para</a>
      <a href="#csvs">CSVs</a>
    </nav>
    """
    body = [
        "<!DOCTYPE html><html lang='pt-BR'><head>",
        "<meta charset='utf-8'>",
        "<title>Relatório UPA Curitiba</title>",
        f"<style>{css}</style></head><body>",
        wrapper_open,
        "<header><h1>Perfil epidemiológico UPA Curitiba</h1>",
        f'<p class="meta">Gerado em {now}</p>',
        toc if theme == "minimal" else "",
        "</header>",
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
    classic = REPORTS_DIR / "profile_report.html"
    minimal = REPORTS_DIR / "profile_report_minimal.html"
    classic.write_text(generate_html("classic"), encoding="utf-8")
    minimal.write_text(generate_html("minimal"), encoding="utf-8")
    print(f"Relatórios gerados:\n  {classic}\n  {minimal}")


if __name__ == "__main__":
    main()
