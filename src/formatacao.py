# [IA] Claude Code (Claude Opus 5.5) – formatação de números no padrão brasileiro e paleta do app
"""Formatação pt-BR, nomes das variáveis e paleta de cores compartilhada pelos dois dashboards."""

import math

import altair as alt

# Locale do Vega-Lite: eixos e tooltips com vírgula decimal e ponto no milhar
LOCALE_PT = {
    "number": {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["R$ ", ""]},
    "time": {
        "dateTime": "%A, %e de %B de %Y. %X",
        "date": "%d/%m/%Y",
        "time": "%H:%M:%S",
        "periods": ["AM", "PM"],
        "days": ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"],
        "shortDays": ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"],
        "months": [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
        ],
        "shortMonths": ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"],
    },
}

MESES_CURTOS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_LONGOS = LOCALE_PT["time"]["months"]
ESTACOES = ["Verão", "Outono", "Inverno", "Primavera"]

# ---------------------------------------------------------------- paleta
# Paleta de referência validada (skill de dataviz): categórica em ordem fixa, divergente azul↔vermelho
# com meio cinza, sequencial de um tom só e cores de status reservadas para os níveis de umidade.
COR_PRINCIPAL = "#2a78d6"   # série única (barras, histogramas)
COR_SECUNDARIA = "#eb6834"  # segunda série
COR_CONTEXTO = "#b4b2ab"    # barras de contexto (anos fora de foco)
COR_REFERENCIA = "#52514e"  # linhas de referência (mediana, média, limiar)
DIVERGENTE = ["#d03b3b", "#f0efec", "#2a78d6"]  # −1 → 0 → +1
SEQUENCIAL_SECO = "oranges"  # % de horas com ar seco (um tom só, claro → escuro)

# Níveis de umidade relativa baixa (status: atenção / alerta / emergência)
NIVEIS_UMIDADE = ["Atenção (21–30%)", "Alerta (12–20%)", "Emergência (<12%)"]
CORES_NIVEIS = ["#fab219", "#ec835a", "#d03b3b"]


def numero(valor, casas: int = 0) -> str:
    """1234567.8 → '1.234.567,8'. NaN/None → '—'."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    texto = f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    # Evita "-0" / "-0,00" quando o valor arredondado é zero
    if texto.startswith("-") and set(texto[1:]) <= set("0,."):
        texto = texto[1:]
    return texto


def percentual(fracao, casas: int = 1) -> str:
    """0.1234 → '12,3%'."""
    if fracao is None or (isinstance(fracao, float) and math.isnan(fracao)):
        return "—"
    return f"{numero(fracao * 100, casas)}%"


def em_portugues(grafico: alt.TopLevelMixin) -> alt.TopLevelMixin:
    """Aplica o locale brasileiro ao gráfico final (último passo antes do st.altair_chart)."""
    return grafico.configure(locale=LOCALE_PT).configure_view(stroke=None)
