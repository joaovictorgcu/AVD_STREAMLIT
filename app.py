# [IA] Claude Code (Claude Opus 5.5) – estrutura do app e abas dos dois dashboards
"""Clima de Brasília (INMET A001, 2014–2023) — dois dashboards em abas.

Rodar localmente:  streamlit run app.py
"""

import streamlit as st

from src import dashboard1, dashboard2
from src.data_loader import load_daily, load_data

st.set_page_config(
    page_title="Clima de Brasília · Dashboards AVD",
    page_icon=":material/partly_cloudy_day:",
    layout="wide",
)

df_horario = load_data()
df_diario = load_daily(df_horario)

st.title("Clima de Brasília · 2014–2023")
st.caption("Estação automática A001 do INMET · dados horários em hora local (UTC−3)")

# Com on_change="rerun", só a aba aberta é executada: a sidebar mostra apenas os filtros dela.
aba_lab, aba_kpi = st.tabs(
    [":material/query_stats: Laboratório de distribuição e correlação", ":material/speed: Painel do tempo seco"],
    key="aba",
    on_change="rerun",
)

if aba_lab.open:
    with aba_lab:
        dashboard1.render(df_horario, df_diario)

if aba_kpi.open:
    with aba_kpi:
        dashboard2.render(df_horario, df_diario)
