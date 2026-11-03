# [IA] Claude Code (Claude Opus 5.5) – fórmulas dos KPIs e agregações do Dashboard 2 (sem Streamlit, testáveis)
"""Indicadores do Dashboard 2 — painel do tempo seco para vigilância em saúde e Defesa Civil.

As definições abaixo são as mesmas documentadas em entregas/justificativa-metricas.md.

Faixas de umidade relativa (UR) baixa, na classificação usada pela Defesa Civil:
    atenção     21 % a 30 %
    alerta      12 % a 20 %
    emergência  abaixo de 12 %
Um dia é classificado pela **menor** UR horária registrada nele.
Dia sem chuva = chuva total do dia < 1,0 mm (abaixo disso a chuva não chega a molhar o solo de forma útil;
é o limiar usual de "dia seco" em climatologia).
"""

import numpy as np
import pandas as pd

from src.formatacao import NIVEIS_UMIDADE

LIMIAR_AR_SECO = 30  # UR ≤ 30 % → atenção ou pior
LIMIAR_ALERTA = 20  # UR ≤ 20 % → alerta ou pior
LIMIAR_EMERGENCIA = 12  # UR < 12 % → emergência
LIMIAR_DIA_SEM_CHUVA_MM = 1.0


def nivel_umidade(ur_min: float) -> str | None:
    """Nível do dia a partir da UR mínima (None = sem restrição ou sem dado)."""
    if pd.isna(ur_min) or ur_min > LIMIAR_AR_SECO:
        return None
    if ur_min < LIMIAR_EMERGENCIA:
        return NIVEIS_UMIDADE[2]
    if ur_min <= LIMIAR_ALERTA:
        return NIVEIS_UMIDADE[1]
    return NIVEIS_UMIDADE[0]


def maior_sequencia(datas: pd.Series, condicao: pd.Series) -> tuple[int, pd.Timestamp | None, pd.Timestamp | None]:
    """Maior sequência de dias **consecutivos no calendário** em que a condição é verdadeira.

    Um dia ausente (ou com condição NaN) interrompe a sequência — não presumo que um dia sem dado foi seco.
    """
    tabela = pd.DataFrame({"data": pd.to_datetime(datas).values, "ok": condicao.values}).sort_values("data")
    melhor, inicio_melhor, fim_melhor = 0, None, None
    atual, inicio_atual, anterior = 0, None, None
    for data, ok in zip(tabela["data"], tabela["ok"]):
        consecutivo = anterior is not None and (data - anterior) == pd.Timedelta(days=1)
        if isinstance(ok, (bool, np.bool_)) and ok:
            if atual > 0 and consecutivo:
                atual += 1
            else:
                atual, inicio_atual = 1, data
            if atual > melhor:
                melhor, inicio_melhor, fim_melhor = atual, inicio_atual, data
        else:
            atual = 0
        anterior = data
    return melhor, inicio_melhor, fim_melhor


def dia_sem_chuva(diario: pd.DataFrame) -> pd.Series:
    """True/False por dia; NaN quando a chuva do dia não pôde ser calculada."""
    return diario["chuva_total"].lt(LIMIAR_DIA_SEM_CHUVA_MM).where(diario["chuva_total"].notna())


def indicadores_por_ano(diario: pd.DataFrame, horario: pd.DataFrame) -> pd.DataFrame:
    """Os KPIs calculados ano a ano (base para a média de referência e para o gráfico anual)."""
    linhas = []
    for ano in sorted(diario["ano"].unique()):
        d = diario[diario["ano"] == ano]
        h = horario[horario["ano"] == ano]
        sem_chuva = dia_sem_chuva(d)
        estiagem, inicio, fim = maior_sequencia(d["data"], sem_chuva)
        ur = h["umidade"].dropna()
        linhas.append(
            {
                "ano": int(ano),
                "dias_ar_seco": int((d["umidade_min"] <= LIMIAR_AR_SECO).sum()),
                "dias_alerta": int((d["umidade_min"] <= LIMIAR_ALERTA).sum()),
                "pct_horas_ar_seco": (ur <= LIMIAR_AR_SECO).mean() if len(ur) else np.nan,
                "maior_estiagem": estiagem,
                "estiagem_inicio": inicio,
                "estiagem_fim": fim,
                "chuva_total": d["chuva_total"].sum(),
                "dias_validos": int(d["umidade_min"].notna().sum()),
            }
        )
    return pd.DataFrame(linhas)


def hora_mais_seca(horario: pd.DataFrame) -> tuple[int | None, float]:
    """Hora local com a maior fração de horas com UR ≤ 30 %."""
    validos = horario.dropna(subset=["umidade"])
    if validos.empty:
        return None, np.nan
    fracao = (validos["umidade"] <= LIMIAR_AR_SECO).groupby(validos["hora"]).mean()
    if fracao.max() == 0:
        return None, 0.0
    return int(fracao.idxmax()), float(fracao.max())


def mapa_mes_hora(horario: pd.DataFrame) -> pd.DataFrame:
    """% das horas com UR ≤ 30 % em cada combinação mês × hora local."""
    validos = horario.dropna(subset=["umidade"])
    tabela = (
        validos.assign(seco=validos["umidade"] <= LIMIAR_AR_SECO)
        .groupby(["mes", "hora"])
        .agg(pct=("seco", "mean"), horas=("seco", "size"))
        .reset_index()
    )
    return tabela


def dias_por_nivel_mes(diario: pd.DataFrame, n_anos: int) -> pd.DataFrame:
    """Média de dias por ano, em cada mês, em cada nível de umidade baixa."""
    niveis = diario["umidade_min"].map(nivel_umidade)
    contagem = (
        diario.assign(nivel=niveis)
        .dropna(subset=["nivel"])
        .groupby(["mes", "nivel"])
        .size()
        .rename("dias")
        .reset_index()
    )
    contagem["dias_por_ano"] = contagem["dias"] / max(n_anos, 1)
    return contagem


def ciclo_diario(horario: pd.DataFrame) -> pd.DataFrame:
    """Mediana e percentil 10 da UR por hora local (o P10 mostra como ficam as horas mais secas)."""
    validos = horario.dropna(subset=["umidade"])
    g = validos.groupby("hora")["umidade"]
    tabela = pd.concat({"Mediana": g.median(), "10% mais secas (P10)": g.quantile(0.10)}, axis=1)
    return tabela.reset_index().melt(id_vars="hora", var_name="serie", value_name="umidade")
