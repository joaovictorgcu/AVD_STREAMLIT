# [IA] Claude Code (Claude Opus 5.5) – leitura do CSV tratado e agregação diária, com cache
"""Leitura do dataset tratado (exportado por notebooks/eda-com-downloads.ipynb)."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "clean" / "dataset.csv"

# Um dia só entra nos indicadores diários se tiver pelo menos esta quantidade de horas medidas.
# Com menos que isso, mínimo/máximo/total do dia ficariam enviesados (ex.: dia com 3 horas).
MIN_HORAS_DIA = 20


@st.cache_data(show_spinner="Carregando os dados do INMET...")
def load_data(path: str | Path = CAMINHO_PADRAO) -> pd.DataFrame:
    """Dataset horário: uma linha por hora local (UTC−3) de 2014 a 2023."""
    df = pd.read_csv(path, parse_dates=["data_hora", "data"])
    return df


def _agrega_com_minimo(serie: pd.Series, func: str) -> float:
    validos = serie.dropna()
    if len(validos) < MIN_HORAS_DIA:
        return np.nan
    return getattr(validos, func)()


@st.cache_data(show_spinner="Agregando por dia...")
def load_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por dia local, com os resumos usados nos dois dashboards.

    Cada resumo só é calculado quando o dia tem pelo menos MIN_HORAS_DIA horas válidas
    da variável; caso contrário fica NaN (dia incompleto não entra na conta).
    """
    return agrega_diario(df)


def agrega_diario(df: pd.DataFrame) -> pd.DataFrame:
    """Versão sem cache de load_daily (usada também nos testes)."""
    g = df.groupby("data")
    diario = pd.DataFrame(
        {
            "temp_media": g["temperatura"].agg(lambda s: _agrega_com_minimo(s, "mean")),
            "temp_max": g["temperatura"].agg(lambda s: _agrega_com_minimo(s, "max")),
            "temp_min": g["temperatura"].agg(lambda s: _agrega_com_minimo(s, "min")),
            "umidade_media": g["umidade"].agg(lambda s: _agrega_com_minimo(s, "mean")),
            "umidade_min": g["umidade"].agg(lambda s: _agrega_com_minimo(s, "min")),
            "chuva_total": g["precipitacao"].agg(lambda s: _agrega_com_minimo(s, "sum")),
            "orvalho_medio": g["ponto_orvalho"].agg(lambda s: _agrega_com_minimo(s, "mean")),
            "horas_medidas": g["temperatura"].size(),
        }
    )
    diario["amplitude_termica"] = diario["temp_max"] - diario["temp_min"]
    diario = diario.reset_index()
    diario["ano"] = diario["data"].dt.year
    diario["mes"] = diario["data"].dt.month
    # Mesmo calendário do dado horário
    calendario = df.drop_duplicates("data").set_index("data")[["estacao", "periodo"]]
    diario = diario.join(calendario, on="data")
    return diario
