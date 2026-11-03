# [IA] Claude Code (Claude Opus 5.5) – testes do dataset tratado (consistência com a EDA original)
"""O dataset do app precisa ser o mesmo da EDA da Aula 11, só com os acréscimos documentados."""

import numpy as np
import pandas as pd

COLUNAS_ESPERADAS = [
    "data_hora", "data", "ano", "mes", "hora", "estacao", "periodo",
    "temperatura", "umidade", "precipitacao", "ponto_orvalho",
]


def test_colunas_e_tamanho(horario):
    assert list(horario.columns) == COLUNAS_ESPERADAS
    # 87.582 linhas da EDA − 3 horas que caem em 31/12/2013 na hora local
    assert len(horario) == 87_579


def test_sem_duplicadas_e_ordenado(horario):
    assert not horario.duplicated().any()
    assert not horario["data_hora"].duplicated().any()
    assert horario["data_hora"].is_monotonic_increasing


def test_periodo_em_hora_local(horario):
    assert horario["data_hora"].min() == pd.Timestamp("2014-01-01 00:00")
    assert horario["data_hora"].max() == pd.Timestamp("2023-12-31 20:00")
    assert set(horario["ano"].unique()) == set(range(2014, 2024))


def test_sentinela_tratada_como_ausente(horario):
    medidas = horario[["temperatura", "umidade", "precipitacao"]]
    assert (medidas == -9999).sum().sum() == 0
    # Mesmas contagens de ausentes da EDA (20 de umidade, 21 de chuva); temperatura sem ausentes
    assert medidas.isna().sum().to_dict() == {"temperatura": 0, "umidade": 20, "precipitacao": 21}


def test_estatisticas_batem_com_a_eda(horario):
    assert round(horario["temperatura"].mean(), 2) == 21.59
    assert round(horario["umidade"].mean(), 2) == 64.43
    assert round(horario["temperatura"].corr(horario["umidade"]), 2) == -0.68
    assert horario["umidade"].dropna().between(0, 100).all()
    assert (horario["precipitacao"].dropna() >= 0).all()


def test_ciclo_diario_em_hora_local(horario):
    """Em hora local o pico de temperatura é à tarde e o mínimo antes do nascer do sol."""
    media = horario.groupby("hora")["temperatura"].mean()
    assert media.idxmax() in (14, 15, 16)
    assert media.idxmin() in (5, 6, 7)


def test_calendario(horario):
    assert set(horario["estacao"]) == {"Verão", "Outono", "Inverno", "Primavera"}
    seco = horario["periodo"] == "Seco (mai–set)"
    assert horario.loc[seco, "mes"].between(5, 9).all()
    assert not horario.loc[~seco, "mes"].between(5, 9).any()


def test_ponto_de_orvalho_nao_supera_temperatura(horario):
    validos = horario.dropna(subset=["ponto_orvalho"])
    # Arredondamento de 0,1 °C quando a UR é 100 %
    assert (validos["ponto_orvalho"] <= validos["temperatura"] + 0.1).all()


def test_sem_dados_pessoais(horario):
    """Só medições meteorológicas e calendário: nenhuma coluna de texto livre ou identificador."""
    texto = horario.select_dtypes(include=["object", "string"]).columns
    assert set(texto) <= {"estacao", "periodo"}


def test_agregacao_diaria(diario):
    # 3.652 dias no calendário 2014–2023; 03/01/2018 não tem nenhuma hora com temperatura no arquivo original
    assert len(diario) == 3651
    calendario = pd.date_range("2014-01-01", "2023-12-31", freq="D")
    assert list(calendario.difference(diario["data"])) == [pd.Timestamp("2018-01-03")]
    assert diario["data"].is_unique
    completos = diario.dropna(subset=["temp_max", "temp_min"])
    assert (completos["temp_max"] >= completos["temp_min"]).all()
    assert np.allclose(completos["amplitude_termica"], completos["temp_max"] - completos["temp_min"])
    # Dias com menos de 20 horas medidas não têm resumo
    incompletos = diario[diario["horas_medidas"] < 20]
    assert incompletos["temp_max"].isna().all()
