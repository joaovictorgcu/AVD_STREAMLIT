# [IA] Claude Code (Claude Opus 5.5) – testes das funções estatísticas e das fórmulas dos KPIs
import numpy as np
import pandas as pd
import pytest

from src import estatisticas as est
from src import indicadores as ind
from src.formatacao import NIVEIS_UMIDADE, numero, percentual

# ------------------------------------------------------------------ formatação


def test_numero_padrao_brasileiro():
    assert numero(1234567.891, 2) == "1.234.567,89"
    assert numero(-0.001, 2) == "0,00"
    assert numero(2.5, 1, sinal=True) == "+2,5"
    assert numero(0, 1, sinal=True) == "0,0"
    assert numero(float("nan")) == "—"
    assert percentual(0.1234) == "12,3%"


# ------------------------------------------------------------------ estatísticas


def test_correlacao_confere_com_pandas(horario):
    cols = ["temperatura", "umidade", "precipitacao"]
    corr = est.matriz_correlacao(horario, cols, "pearson")
    pd.testing.assert_frame_equal(corr, horario[cols].corr())
    assert round(corr.loc["temperatura", "umidade"], 2) == -0.68
    spear = est.matriz_correlacao(horario, cols, "spearman")
    pd.testing.assert_frame_equal(spear, horario[cols].corr(method="spearman"))


def test_correlacao_com_variavel_constante():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [5, 5, 5, 5], "c": [4, 3, 2, 1]})
    corr = est.matriz_correlacao(df, ["a", "b", "c"])
    assert np.isnan(corr.loc["a", "b"])
    assert corr.loc["a", "c"] == pytest.approx(-1)
    pares = est.pares_ordenados(corr)
    assert pares.iloc[0]["forca"] == "muito forte"
    assert pares["r"].isna().sum() == 2  # pares com a constante ficam por último, indefinidos


def test_correlacao_longa_triangulo_inferior():
    corr = pd.DataFrame(np.eye(3), index=list("xyz"), columns=list("xyz"))
    longa = est.correlacao_longa(corr)
    assert len(longa) == 6  # n(n+1)/2


@pytest.mark.parametrize(
    "r, esperado",
    [(0.05, "desprezível"), (-0.2, "fraca"), (0.4, "moderada"), (-0.68, "forte"), (0.78, "muito forte")],
)
def test_forca_correlacao(r, esperado):
    assert est.forca_correlacao(r) == esperado


def test_descritivas_e_outliers_iqr(horario):
    desc = est.descritivas(horario, ["temperatura", "umidade", "precipitacao"]).set_index("variavel")
    # Mesmos números de outliers por IQR da EDA da Aula 11 (calculados antes de remover as 3 horas de 2013)
    assert desc.loc["umidade", "outliers"] == 0
    assert 300 <= desc.loc["temperatura", "outliers"] <= 303
    assert 5380 <= desc.loc["precipitacao", "outliers"] <= 5383
    assert bool(desc.loc["precipitacao", "iqr_nulo"]) is True
    assert desc.loc["precipitacao", "forma"] == "forte à direita"
    assert desc.loc["temperatura", "forma"] == "aprox. simétrica"
    assert desc.loc["umidade", "ausentes"] == 20


def test_descritivas_variavel_vazia_e_constante():
    df = pd.DataFrame({"vazia": [np.nan, np.nan], "const": [3.0, 3.0]})
    desc = est.descritivas(df, ["vazia", "const"]).set_index("variavel")
    assert desc.loc["vazia", "n"] == 0
    assert desc.loc["const", "forma"] == "indefinida"


def test_histograma_soma_e_casos_de_borda(horario):
    h = est.histograma(horario["temperatura"], 30)
    assert h["contagem"].sum() == horario["temperatura"].notna().sum()
    assert len(h) == 30
    assert h["pct"].sum() == pytest.approx(1)
    # Inteiros: faixas de largura inteira, sem "pente"
    hi = est.histograma(horario["umidade"], 30, inteiro=True)
    assert hi["contagem"].sum() == horario["umidade"].notna().sum()
    assert np.allclose(np.diff(hi["inicio"]), np.diff(hi["inicio"])[0])
    assert est.histograma(pd.Series([2.0, 2.0]), 10)["contagem"].tolist() == [2]
    assert est.histograma(pd.Series([], dtype=float), 10).empty


def test_densidade_2d_conserva_registros(horario):
    d = est.densidade_2d(horario, "temperatura", "umidade", bins=20)
    assert d["contagem"].sum() == horario[["temperatura", "umidade"]].dropna().shape[0]


def test_resumo_boxplot(horario):
    r = est.resumo_boxplot(horario, "umidade", "estacao", ["Verão", "Inverno"]).set_index("estacao")
    assert r.loc["Inverno", "mediana"] < r.loc["Verão", "mediana"]  # inverno mais seco (EDA)
    assert (r["bigode_inf"] <= r["q1"]).all() and (r["q3"] <= r["bigode_sup"]).all()


# ------------------------------------------------------------------ indicadores (Dashboard 2)


@pytest.mark.parametrize(
    "ur, nivel",
    [(31, None), (30, NIVEIS_UMIDADE[0]), (21, NIVEIS_UMIDADE[0]), (20, NIVEIS_UMIDADE[1]),
     (12, NIVEIS_UMIDADE[1]), (11, NIVEIS_UMIDADE[2]), (np.nan, None)],
)
def test_nivel_umidade(ur, nivel):
    assert ind.nivel_umidade(ur) == nivel


def test_maior_sequencia_respeita_calendario():
    datas = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-05", "2020-01-06"])
    tamanho, inicio, fim = ind.maior_sequencia(pd.Series(datas), pd.Series([True, True, True, True, True]))
    assert (tamanho, inicio, fim) == (3, pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03"))
    # NaN interrompe a sequência
    t2, _, _ = ind.maior_sequencia(pd.Series(datas[:3]), pd.Series([True, np.nan, True], dtype=object))
    assert t2 == 1
    assert ind.maior_sequencia(pd.Series(datas[:2]), pd.Series([False, False]))[0] == 0


def test_kpis_por_ano_conferem_com_calculo_direto(horario, diario):
    por_ano = ind.indicadores_por_ano(diario, horario).set_index("ano")
    d15 = diario[diario["ano"] == 2015]
    assert por_ano.loc[2015, "dias_ar_seco"] == (d15["umidade_min"] <= 30).sum()
    assert por_ano.loc[2015, "dias_alerta"] == (d15["umidade_min"] <= 20).sum()
    h15 = horario[horario["ano"] == 2015]["umidade"].dropna()
    assert por_ano.loc[2015, "pct_horas_ar_seco"] == pytest.approx((h15 <= 30).mean())
    # Chuva anual: mesma ordem de grandeza da EDA (2021 foi o ano mais chuvoso)
    assert por_ano["chuva_total"].idxmax() == 2021
    assert (por_ano["dias_alerta"] <= por_ano["dias_ar_seco"]).all()
    assert len(por_ano) == 10


def test_estiagem_no_periodo_seco(horario, diario):
    por_ano = ind.indicadores_por_ano(diario, horario)
    linha = por_ano.loc[por_ano["maior_estiagem"].idxmax()]
    # A maior estiagem cai no período seco
    assert 4 <= linha["estiagem_inicio"].month <= 6
    assert 8 <= linha["estiagem_fim"].month <= 10


def test_hora_mais_seca_e_mapa(horario):
    hora, frac = ind.hora_mais_seca(horario)
    assert hora in (14, 15, 16)
    mapa = ind.mapa_mes_hora(horario)
    assert len(mapa) == 12 * 24
    assert mapa["pct"].between(0, 1).all()
    assert mapa.loc[mapa["pct"].idxmax(), "mes"] in (8, 9)
    # A fração da hora mais seca é a média ponderada (por horas medidas) da coluna dessa hora no mapa
    coluna = mapa[mapa["hora"] == hora]
    assert frac == pytest.approx((coluna["pct"] * coluna["horas"]).sum() / coluna["horas"].sum())


def test_dias_por_nivel_mes(diario):
    tabela = ind.dias_por_nivel_mes(diario, 10)
    total = tabela["dias"].sum()
    assert total == (diario["umidade_min"] <= 30).sum()
    assert set(tabela["nivel"]) <= set(NIVEIS_UMIDADE)


def test_ciclo_diario(horario):
    ciclo = ind.ciclo_diario(horario).pivot(index="hora", columns="serie", values="umidade")
    assert (ciclo["10% mais secas (P10)"] <= ciclo["Mediana"]).all()
