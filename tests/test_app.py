# [IA] Claude Code (Claude Opus 5.5) – testes do app com o streamlit.testing (abas, widgets e casos de borda)
"""Executa o app.py de verdade (sem navegador) e interage com os widgets."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 180


def novo_app() -> AppTest:
    return AppTest.from_file(APP, default_timeout=TIMEOUT)


def sem_erros(at: AppTest):
    assert not at.exception, [e.value for e in at.exception]


def widget(colecao, rotulo):
    for w in colecao:
        if w.label == rotulo:
            return w
    raise KeyError(rotulo)


def metricas(at):
    return {m.label: m.value for m in at.metric}


# ------------------------------------------------------------------ Dashboard 1


@pytest.fixture
def lab():
    at = novo_app().run()
    sem_erros(at)
    return at


def test_abre_no_laboratorio(lab):
    assert [t.label.split(": ")[-1] for t in lab.tabs] == [
        "Laboratório de distribuição e correlação",
        "Painel do tempo seco",
    ]
    assert metricas(lab)["Registros avaliados (horas)"] == "87.579"
    assert widget(lab.sidebar.multiselect, "Variáveis avaliadas").value == [
        "temperatura", "umidade", "precipitacao", "ponto_orvalho",
    ]
    assert len(lab.dataframe) == 1  # tabela de estatísticas


def test_zero_variaveis(lab):
    widget(lab.sidebar.multiselect, "Variáveis avaliadas").set_value([]).run()
    sem_erros(lab)
    assert any("pelo menos uma variável" in i.value for i in lab.info)


def test_uma_variavel(lab):
    widget(lab.sidebar.multiselect, "Variáveis avaliadas").set_value(["umidade"]).run()
    sem_erros(lab)
    assert any("pelo menos duas variáveis" in i.value for i in lab.info)
    assert len(lab.dataframe) == 1


def test_slider_de_intervalo_filtra(lab):
    slider = widget(lab.sidebar.slider, "Intervalo de temperatura (°C)")
    slider.set_value((20.0, 25.0)).run()
    sem_erros(lab)
    import pandas as pd

    df = pd.read_csv(Path(APP).parent / "data" / "clean" / "dataset.csv")
    esperado = int(df["temperatura"].between(20.0, 25.0).sum())
    m = metricas(lab)
    assert m["Registros avaliados (horas)"] == f"{esperado:,}".replace(",", ".")
    assert m["Excluídos pelo intervalo"] == f"{len(df) - esperado:,}".replace(",", ".")


def test_slider_intervalo_minimo_gera_constante(lab):
    """Intervalo de um único valor: temperatura fica constante → correlação indefinida, sem erro."""
    widget(lab.sidebar.slider, "Intervalo de temperatura (°C)").set_value((21.0, 21.0)).run()
    sem_erros(lab)
    assert any("constante" in m.value for m in lab.markdown)


def test_trocar_variavel_do_intervalo(lab):
    widget(lab.sidebar.selectbox, "Variável do intervalo").set_value("umidade").run()
    sem_erros(lab)
    widget(lab.sidebar.slider, "Intervalo de umidade relativa (%)").set_value((10.0, 30.0)).run()
    sem_erros(lab)
    assert metricas(lab)["Registros avaliados (horas)"] != "87.579"


def test_sem_estacoes_e_anos(lab):
    widget(lab.sidebar.button_group, "Estações do ano").set_value([]).run()
    sem_erros(lab)
    assert any("estação" in w.value for w in lab.warning)


def test_um_ano_so(lab):
    widget(lab.sidebar.slider, "Anos").set_value((2021, 2021)).run()
    sem_erros(lab)
    assert metricas(lab)["Período"] == "2021"


def test_granularidade_diaria_e_opcoes(lab, diario):
    widget(lab.sidebar.button_group, "Granularidade").set_value("Diária").run()
    sem_erros(lab)
    # Padrão do intervalo = temperatura máxima: dias sem resumo (menos de 20 horas) ficam de fora
    esperado = int(diario["temp_max"].notna().sum())
    assert metricas(lab)["Registros avaliados (dias)"] == f"{esperado:,}".replace(",", ".")
    widget(lab.sidebar.button_group, "Correlação").set_value("spearman").run()
    widget(lab.sidebar.slider, "Faixas dos histogramas").set_value(50).run()
    widget(lab.sidebar.toggle, "Eixo de contagem em escala log").set_value(True).run()
    sem_erros(lab)


def test_comparacao_mesma_variavel(lab):
    widget(lab.selectbox, "Eixo Y").set_value("temperatura").run()
    sem_erros(lab)
    assert any("duas variáveis diferentes" in i.value for i in lab.info)


# ------------------------------------------------------------------ Dashboard 2


@pytest.fixture
def painel():
    at = novo_app().run()
    at.session_state["aba"] = at.tabs[1].label
    at.run()
    sem_erros(at)
    return at


def test_painel_kpis_media(painel):
    m = metricas(painel)
    assert set(m) == {"Dias secos/ano", "Dias em alerta/ano", "Horas de ar seco", "Maior estiagem", "Hora mais seca"}
    assert m["Hora mais seca"] == "15h"
    assert m["Maior estiagem"] == "133 dias"
    assert len(painel.sidebar.selectbox) == 1  # sidebar mostra só os filtros do painel


@pytest.mark.parametrize("ano", list(range(2014, 2024)))
def test_painel_cada_ano(painel, ano):
    widget(painel.sidebar.selectbox, "Ano em foco").set_value(ano).run()
    sem_erros(painel)
    deltas = {m.label: m.delta for m in painel.metric}
    assert deltas["Dias secos"]  # comparação com a média aparece
    assert deltas["Horas de ar seco"].endswith("p.p.")


@pytest.mark.parametrize("recorte", ["Período seco (mai–set)", "Período chuvoso (out–abr)"])
def test_painel_recortes(painel, recorte):
    widget(painel.sidebar.button_group, "Meses considerados").set_value(recorte).run()
    sem_erros(painel)
    widget(painel.sidebar.selectbox, "Ano em foco").set_value(2019).run()
    sem_erros(painel)
