"""Constantes de colunas e tipos do dataset UPA."""

from typing import Final

# Metadados
COL_MES_COLETA: Final = "mes_coleta"

# Demográficas
COL_SEXO: Final = "sexo"
COL_FAIXA_ETARIA: Final = "faixa_etaria"
COL_IDADE_NUMERICA: Final = "idade_numerica"
COL_DATA_NASCIMENTO: Final = "data_nascimento"

# Atendimento
COL_DATA_INICIO: Final = "data_inicio_consulta"
COL_HORA_INICIO: Final = "hora_inicio_consulta"
COL_DATA_FIM: Final = "data_fim_consulta"
COL_HORA_FIM: Final = "hora_fim_consulta"
COL_CID_ADMISSAO: Final = "cid_admissao"
COL_DESC_CID_ADMISSAO: Final = "desc_cid_admissao"
COL_FLUXOGRAMA: Final = "fluxograma"
COL_DISCRIMINADOR: Final = "discriminador"
COL_PRIORIDADE: Final = "prioridade"
COL_SETOR_DESTINADO: Final = "setor_destinado"
COL_TEMPO_PERMANENCIA: Final = "tempo_permanencia"
COL_DURACAO_HORAS: Final = "duracao_horas"
COL_DESFECHO: Final = "desfecho"
COL_DESFECHO_PADRONIZADO: Final = "desfecho_padronizado"

# Comorbidades e hábitos
COL_COMORBIDADE: Final = "comorbidade"
COL_DIABETICO: Final = "diabetico"
COL_HIPERTENSO: Final = "hipertenso"
COL_SAUDE_MENTAL: Final = "saude_mental"
COL_TABAGISTA: Final = "tabagista"
COL_ETILISTA: Final = "etilista"
COL_USO_SPAS: Final = "uso_spas"
COL_DOENCAS_CARDIACAS: Final = "doencas_cardiacas"
COL_DOENCAS_RESPIRATORIAS: Final = "doencas_respiratorias"
COL_NEOPLASIAS: Final = "neoplasias"
COL_DOENCAS_METABOLICAS: Final = "doencas_metabolicas"

# Headers originais do Excel → colunas normalizadas
EXCEL_COL_MAP: Final[dict[str, str]] = {
    "DATA DO INÍCIO DA CONSULTA": COL_DATA_INICIO,
    "INICIO DA CONSULTA": COL_HORA_INICIO,
    "INÍCIO DA CONSULTA": COL_HORA_INICIO,
    "DATA DO FINAL DA CONSULTA": COL_DATA_FIM,
    "FINAL DA CONSULTA": COL_HORA_FIM,
    "DATA DE NASCIMENTO": COL_DATA_NASCIMENTO,
    "IDADE": COL_FAIXA_ETARIA,
    "IDADE.1": COL_IDADE_NUMERICA,
    "SEXO (F / M)": COL_SEXO,
    "CID Admissão": COL_CID_ADMISSAO,
    "FLUXOGRAMA UTILIZADO NA CR": COL_FLUXOGRAMA,
    "DESCRIMINADOR": COL_DISCRIMINADOR,
    "PRIORIDADE": COL_PRIORIDADE,
    "Desc. CID Admissão": COL_DESC_CID_ADMISSAO,
    "SETOR DESTINADO": COL_SETOR_DESTINADO,
    "Data Diagnóstico Admissão": "data_diag_admissao",
    "Desc. CID Alta": "desc_cid_alta",
    "Data Diagnóstico Alta": "data_diag_alta",
    "COMORBIDADE  (SIM OU NÃO)": COL_COMORBIDADE,
    "COMORBIDADES (SIM OU NÃO)": COL_COMORBIDADE,
    "Diabético": COL_DIABETICO,
    "Hipertenso": COL_HIPERTENSO,
    "Saúde mental": COL_SAUDE_MENTAL,
    "TABAGISTA": COL_TABAGISTA,
    "ETILISTA": COL_ETILISTA,
    "USO DE SPAS": COL_USO_SPAS,
    "DOENÇAS CARDÍACAS": COL_DOENCAS_CARDIACAS,
    "DOENÇAS RESPIRATÓRIAS CRÔNICAS": COL_DOENCAS_RESPIRATORIAS,
    "NEOPLASIAS": COL_NEOPLASIAS,
    "DOENÇAS METABÓLICAS": COL_DOENCAS_METABOLICAS,
    "TEMPO TOTAL DE PERMANÊNCIA NA UPA": COL_TEMPO_PERMANENCIA,
    "DESFECHO FINAL": COL_DESFECHO,
}

# Colunas a harmonizar entre abas (alias → canônico)
SHEET_COLUMN_ALIASES: Final[dict[str, str]] = {
    "INÍCIO DA CONSULTA": "INICIO DA CONSULTA",
    "COMORBIDADES (SIM OU NÃO)": "COMORBIDADE  (SIM OU NÃO)",
}

DEMOGRAPHIC_COLS: Final[list[str]] = [
    COL_SEXO,
    COL_FAIXA_ETARIA,
]

CLINICAL_CATEGORICAL_COLS: Final[list[str]] = [
    COL_COMORBIDADE,
    COL_DIABETICO,
    COL_HIPERTENSO,
    COL_SAUDE_MENTAL,
    COL_TABAGISTA,
    COL_ETILISTA,
    COL_USO_SPAS,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_NEOPLASIAS,
    COL_DOENCAS_METABOLICAS,
    COL_SETOR_DESTINADO,
    COL_TEMPO_PERMANENCIA,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
]

CLINICAL_NUMERIC_COLS: Final[list[str]] = [
    COL_IDADE_NUMERICA,
    COL_DURACAO_HORAS,
]

ASSOCIATION_PREDICTORS: Final[list[str]] = [
    COL_COMORBIDADE,
    COL_TABAGISTA,
    COL_ETILISTA,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_DOENCAS_METABOLICAS,
    COL_SETOR_DESTINADO,
    COL_TEMPO_PERMANENCIA,
]

NUMERIC_COLS: Final[list[str]] = [
    COL_IDADE_NUMERICA,
    COL_DURACAO_HORAS,
]

YES_NO_COLS: Final[list[str]] = [
    COL_COMORBIDADE,
    COL_DIABETICO,
    COL_HIPERTENSO,
    COL_SAUDE_MENTAL,
    COL_TABAGISTA,
    COL_ETILISTA,
    COL_USO_SPAS,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_NEOPLASIAS,
    COL_DOENCAS_METABOLICAS,
]

DEPARA_VALUE_COLS: Final[list[str]] = [
    COL_SEXO,
    COL_FAIXA_ETARIA,
    COL_COMORBIDADE,
    COL_DIABETICO,
    COL_HIPERTENSO,
    COL_SAUDE_MENTAL,
    COL_TABAGISTA,
    COL_ETILISTA,
    COL_USO_SPAS,
    COL_DOENCAS_CARDIACAS,
    COL_DOENCAS_RESPIRATORIAS,
    COL_NEOPLASIAS,
    COL_DOENCAS_METABOLICAS,
    COL_SETOR_DESTINADO,
    COL_TEMPO_PERMANENCIA,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
]
