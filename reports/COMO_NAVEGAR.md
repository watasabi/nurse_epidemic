# Como navegar pela pasta `reports/` — guia para a enfermagem

Este guia foi escrito para quem **não programa** e precisa usar os
resultados do estudo da UPA Curitiba (perfil Manchester "muito
urgente", abril–maio/2025, 328 prontuários).

Você não precisa abrir nenhum código. Tudo o que interessa está em
arquivos que abrem no navegador, no Excel ou em qualquer editor de
texto.

## 1. O caminho mais rápido (5 minutos)

Abra o arquivo **`profile_report_minimal.html`** com dois cliques. Ele
abre no navegador (Chrome, Edge, Firefox) e reúne, em uma página só:

- os gráficos do estudo;
- as tabelas de frequência (quantos pacientes em cada categoria);
- os testes estatísticos com explicação;
- o de-para entre a planilha original e os dados padronizados.

No topo da página há uma barra de atalhos (Guias, Associações,
Correlações, Análise clínica, Figuras, De-para, CSVs). Clique para
pular direto à seção desejada.

> **Baixou ou recebeu o HTML por e-mail?** Os gráficos em imagem
> continuam aparecendo, porque ficam gravados dentro do próprio
> arquivo. Só os gráficos interativos (aqueles em que você passa o
> mouse e vê o número) precisam de internet no momento da abertura.

Existe também `profile_report.html`, com o mesmo conteúdo em um visual
mais simples — útil para imprimir ou colar em documento.

## 2. O que existe em cada pasta

| Pasta / arquivo | Para que serve | Quando usar |
|---|---|---|
| `profile_report_minimal.html` | Relatório completo, visual | Leitura geral, reunião |
| `profile_report.html` | Mesmo conteúdo, visual simples | Impressão |
| `descriptive/` | Tabelas em CSV (abrem no Excel) | Números exatos para o artigo |
| `figures/` | Gráficos em PNG | Colar no artigo, slide, pôster |
| `association_results.md` | Explicação dos testes em português | Escrever a discussão |
| `association_results.csv` | Números dos testes | Conferir p-valores |
| `association_phik_matrix.csv` | Força de associação (0 a 1) | Visão geral entre variáveis |
| `correlation_results.md` | Explicação das correlações | Escrever resultados |
| `depara_*.csv` | Como cada valor bruto virou valor padronizado | Auditar / responder revisor |

Cada subpasta tem seu próprio `README.md` com detalhes:

- [`descriptive/README.md`](descriptive/README.md) — significado de
  cada coluna das tabelas;
- [`figures/README.md`](figures/README.md) — o que cada gráfico mostra.

## 3. Como usar as tabelas de `descriptive/`

Os arquivos são CSV: dê dois cliques e eles abrem no Excel ou no
LibreOffice.

O nome do arquivo já diz o assunto:

- começa com **`demo_`** → perfil demográfico (sexo, faixa etária);
- começa com **`clin_`** → dado clínico (comorbidade, hábito, setor,
  tempo de permanência, desfecho).

As colunas mais comuns:

| Coluna | Leitura em português |
|---|---|
| `valor` | A categoria (ex.: ALTA, SIM, EIXO CRITICO) |
| `absoluta` | Quantos pacientes (n) |
| `relativa` | Proporção de 0 a 1 — `0,25` é 25% |
| `sim_absoluta` | Quantos responderam SIM |
| `n_valido` | Quantos prontuários tinham essa informação |

No relatório HTML essas proporções já aparecem convertidas em
porcentagem, para você não precisar calcular.

Para variáveis numéricas (idade, duração), as colunas são `n`,
`media`, `mediana`, `min`, `max` e `desvio_padrao`.

## 4. Como usar os gráficos de `figures/`

São imagens PNG em 120 dpi, prontas para artigo ou apresentação.
Clique com o botão direito → "Copiar imagem" e cole no seu documento.

Se preferir vê-los todos juntos com legenda, use a seção **Figuras**
do relatório HTML.

Na legenda do artigo, cite a fonte: dados da UPA Curitiba
(classificação Manchester, muito urgente), abril–maio/2025.

## 5. Como ler os testes estatísticos

Comece por [`association_results.md`](association_results.md). Ele
explica, sem jargão:

- o que foi testado (cada variável clínica contra o desfecho);
- por que cada teste foi escolhido (χ², Fisher, Kruskal-Wallis);
- o que significa o p-valor;
- quais variáveis tiveram associação significativa.

Regra prática: **p menor que 0,05** indica associação
estatisticamente significativa. Isso não prova causa — significa que
a diferença observada dificilmente seria só acaso.

No HTML, o gráfico de barras da seção "Associações" mostra a mesma
informação: barra mais longa = evidência mais forte. A linha vermelha
tracejada marca o limite de p = 0,05.

A matriz PhiK (mapa de calor azul) é um complemento: vai de 0
(nenhuma associação) a 1 (associação total) entre pares de variáveis.

## 6. Roteiro sugerido para escrever o artigo

1. **Métodos** — descreva a amostra usando `descriptive/demo_*.csv` e
   a padronização documentada em
   [`../docs/depara_normalizacoes.md`](../docs/depara_normalizacoes.md).
2. **Resultados descritivos** — use `clin_desfecho.csv`,
   `clin_setor_destinado.csv`, `clin_comorbidades.csv`,
   `clin_habitos_vida.csv` e `clin_tempo_permanencia.csv`. Sempre cite
   o n junto da porcentagem.
3. **Resultados inferenciais** — use `association_results.md` e a
   tabela `association_results.csv`.
4. **Figuras** — escolha em `figures/` as que ilustram cada parágrafo.
5. **Discussão** — apoie-se nas variáveis significativas e nas
   correlações de `correlation_results.md`.

## 7. Perguntas frequentes

**Os números mudaram, o que faço?**
Peça a quem cuida do código para rodar os dois comandos abaixo na raiz
do projeto. Todos os arquivos desta pasta são regerados
automaticamente:

```bash
uv run python reports/export_clinical_summaries.py
uv run python reports/generate_profile_report.py
```

**Abri o HTML e apareceu um aviso amarelo no topo.**
Significa que a base de dados foi atualizada depois das tabelas. Os
comandos acima resolvem.

**Posso editar os CSVs à mão?**
Não. Eles são recriados a cada execução e sua edição seria perdida.
Copie para outra planilha se precisar fazer contas próprias.

**De onde vêm esses dados?**
Da planilha `data/raw/Planilha de dados- Estátistico.xlsx`, limpa e
padronizada pelo pipeline. Cada transformação está registrada em
`depara_colunas.csv`, `depara_valores.csv` e `depara_regras.csv`.
