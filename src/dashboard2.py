# [IA] Claude Code (Claude Opus 5.5) – Dashboard 2: KPIs do tempo seco, gráficos em Altair e textos de leitura
"""Dashboard 2 — Painel do tempo seco.

Público-alvo: equipes de vigilância em saúde ambiental e de Defesa Civil do Distrito Federal, que planejam
alertas, campanhas e orientações (ex.: suspensão de atividades físicas ao ar livre em escolas) para o
período de umidade baixa. As fórmulas estão em src/indicadores.py e em entregas/justificativa-metricas.md.
"""

import altair as alt
import pandas as pd
import streamlit as st

from src import indicadores as ind
from src.formatacao import (
    COR_CONTEXTO,
    COR_PRINCIPAL,
    COR_REFERENCIA,
    COR_SECUNDARIA,
    CORES_NIVEIS,
    MESES_CURTOS,
    MESES_LONGOS,
    NIVEIS_UMIDADE,
    SEQUENCIAL_SECO,
    em_portugues,
    numero,
    percentual,
)

TODOS = "todos"
RECORTES = {
    "Ano inteiro": list(range(1, 13)),
    "Período seco (mai–set)": [5, 6, 7, 8, 9],
    "Período chuvoso (out–abr)": [10, 11, 12, 1, 2, 3, 4],
}


# ====================================================================== gráficos


def grafico_mapa_mes_hora(tabela: pd.DataFrame, meses: list[int]) -> alt.Chart:
    tabela = tabela.assign(mes_nome=tabela["mes"].map(lambda m: MESES_CURTOS[m - 1]))
    ordem_meses = [MESES_CURTOS[m - 1] for m in sorted(meses)]
    return em_portugues(
        alt.Chart(tabela)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X("hora:O", title="Hora local", axis=alt.Axis(labelAngle=0, labelExpr="datum.value + 'h'")),
            y=alt.Y("mes_nome:N", sort=ordem_meses, title=None),
            color=alt.Color(
                "pct:Q",
                scale=alt.Scale(scheme=SEQUENCIAL_SECO, domain=[0, max(0.6, float(tabela["pct"].max() or 0))]),
                legend=alt.Legend(title="% das horas", format=".0%", gradientLength=150),
            ),
            tooltip=[
                alt.Tooltip("mes_nome:N", title="Mês"),
                alt.Tooltip("hora:O", title="Hora"),
                alt.Tooltip("pct:Q", title="Horas com UR ≤ 30%", format=".1%"),
                alt.Tooltip("horas:Q", title="Horas medidas", format=","),
            ],
        )
        .properties(height=34 * len(ordem_meses) + 30)
    )


def grafico_niveis_mes(tabela: pd.DataFrame, meses: list[int], titulo_y: str) -> alt.Chart:
    base = pd.DataFrame(
        [(m, n) for m in sorted(meses) for n in NIVEIS_UMIDADE], columns=["mes", "nivel"]
    )
    tabela = base.merge(tabela, on=["mes", "nivel"], how="left").fillna({"dias": 0, "dias_por_ano": 0})
    tabela["mes_nome"] = tabela["mes"].map(lambda m: MESES_CURTOS[m - 1])
    tabela["ordem_nivel"] = tabela["nivel"].map(NIVEIS_UMIDADE.index)
    return em_portugues(
        alt.Chart(tabela)
        .mark_bar()
        .encode(
            x=alt.X("mes_nome:N", sort=[MESES_CURTOS[m - 1] for m in sorted(meses)], title=None,
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y("dias_por_ano:Q", title=titulo_y, stack="zero"),
            color=alt.Color(
                "nivel:N",
                scale=alt.Scale(domain=NIVEIS_UMIDADE, range=CORES_NIVEIS),
                legend=alt.Legend(title="Nível do dia (UR mínima)", orient="top", columns=2, labelLimit=180),
            ),
            order=alt.Order("ordem_nivel:Q"),
            tooltip=[
                alt.Tooltip("mes_nome:N", title="Mês"),
                alt.Tooltip("nivel:N", title="Nível"),
                alt.Tooltip("dias_por_ano:Q", title=titulo_y, format=",.1f"),
            ],
        )
        .properties(height=290)
    )


def grafico_anual(por_ano: pd.DataFrame, foco) -> alt.Chart:
    tabela = por_ano.assign(
        destaque=por_ano["ano"].map(lambda a: "foco" if foco == TODOS or a == foco else "contexto"),
        ano_txt=por_ano["ano"].astype(str),
    )
    media = tabela["dias_ar_seco"].mean()
    barras = (
        alt.Chart(tabela)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("ano_txt:O", title=None, axis=alt.Axis(labelAngle=0), scale=alt.Scale(paddingInner=0.35)),
            y=alt.Y("dias_ar_seco:Q", title="Dias com UR mínima ≤ 30%"),
            color=alt.Color(
                "destaque:N", scale=alt.Scale(domain=["foco", "contexto"], range=[COR_PRINCIPAL, COR_CONTEXTO]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("ano_txt:O", title="Ano"),
                alt.Tooltip("dias_ar_seco:Q", title="Dias com ar seco"),
                alt.Tooltip("dias_alerta:Q", title="Dias em alerta ou pior"),
                alt.Tooltip("maior_estiagem:Q", title="Maior estiagem (dias)"),
                alt.Tooltip("chuva_total:Q", title="Chuva no recorte (mm)", format=",.0f"),
            ],
        )
    )
    regra = (
        alt.Chart(pd.DataFrame({"media": [media]}))
        .mark_rule(color=COR_REFERENCIA, strokeWidth=1.5)
        .encode(y="media:Q", tooltip=[alt.Tooltip("media:Q", title="Média 2014–2023", format=",.1f")])
    )
    return em_portugues((barras + regra).properties(height=290))


def grafico_ciclo(tabela: pd.DataFrame) -> alt.Chart:
    series = ["Mediana", "10% mais secas (P10)"]
    linhas = (
        alt.Chart(tabela)
        .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=36, filled=True))
        .encode(
            x=alt.X("hora:Q", title="Hora local", scale=alt.Scale(domain=[0, 23], nice=False),
                    axis=alt.Axis(values=list(range(0, 24, 3)), labelExpr="datum.value + 'h'")),
            y=alt.Y("umidade:Q", title="Umidade relativa (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "serie:N", scale=alt.Scale(domain=series, range=[COR_PRINCIPAL, COR_SECUNDARIA]),
                legend=alt.Legend(title=None, orient="top", direction="horizontal"),
            ),
            tooltip=[
                alt.Tooltip("hora:Q", title="Hora"),
                alt.Tooltip("serie:N", title="Série"),
                alt.Tooltip("umidade:Q", title="UR (%)", format=",.0f"),
            ],
        )
    )
    limiar = pd.DataFrame({"y": [ind.LIMIAR_AR_SECO], "texto": ["30% · atenção"]})
    regra = alt.Chart(limiar).mark_rule(color=CORES_NIVEIS[2], strokeWidth=1.5).encode(y="y:Q")
    texto = (
        alt.Chart(limiar)
        .mark_text(align="left", dx=4, dy=-7, color=CORES_NIVEIS[2], fontSize=11)
        .encode(y="y:Q", x=alt.value(0), text="texto:N")
    )
    return em_portugues((regra + texto + linhas).properties(height=290))


# ====================================================================== KPIs


def _delta(valor, referencia, casas=1, sufixo=""):
    if referencia is None or pd.isna(referencia) or pd.isna(valor):
        return None
    return f"{numero(valor - referencia, casas, sinal=True)}{sufixo}"


def mostra_kpis(diario, horario, por_ano, foco, recorte):
    n_anos = 1 if foco != TODOS else len(por_ano)
    dias_seco = int((diario["umidade_min"] <= ind.LIMIAR_AR_SECO).sum()) / n_anos
    dias_alerta = int((diario["umidade_min"] <= ind.LIMIAR_ALERTA).sum()) / n_anos
    ur = horario["umidade"].dropna()
    pct_horas = (ur <= ind.LIMIAR_AR_SECO).mean() if len(ur) else float("nan")
    estiagem, ini, fim = ind.maior_sequencia(diario["data"], ind.dia_sem_chuva(diario))
    hora, pct_hora = ind.hora_mais_seca(horario)

    media = por_ano[["dias_ar_seco", "dias_alerta", "pct_horas_ar_seco", "maior_estiagem"]].mean()
    comparar = foco != TODOS
    descricao = "vs. média 2014–2023" if comparar else None
    rotulo_ano = "" if comparar else "/ano"

    periodo_estiagem = (
        f"de {ini:%d/%m/%Y} a {fim:%d/%m/%Y}" if estiagem and ini is not None else "sem dias sem chuva no recorte"
    )
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(
            f"Dias secos{rotulo_ano}",
            numero(dias_seco, 0 if comparar else 1),
            _delta(dias_seco, media["dias_ar_seco"] if comparar else None),
            delta_color="inverse",
            delta_description=descricao,
            chart_data=por_ano["dias_ar_seco"].tolist(),
            chart_type="bar",
            border=True,
            help="Dias cuja umidade relativa mínima ficou em 30% ou menos (estado de atenção ou pior). "
            f"Recorte: {recorte.lower()}. Minigráfico: um valor por ano, 2014–2023.",
        )
    with c2:
        st.metric(
            f"Dias em alerta{rotulo_ano}",
            numero(dias_alerta, 0 if comparar else 1),
            _delta(dias_alerta, media["dias_alerta"] if comparar else None),
            delta_color="inverse",
            delta_description=descricao,
            chart_data=por_ano["dias_alerta"].tolist(),
            chart_type="bar",
            border=True,
            help="Dias com umidade relativa mínima de 20% ou menos (alerta ou emergência).",
        )
    with c3:
        st.metric(
            "Horas de ar seco",
            percentual(pct_horas),
            _delta(pct_horas * 100, media["pct_horas_ar_seco"] * 100 if comparar else None, 1, " p.p."),
            delta_color="inverse",
            delta_description=descricao,
            chart_data=(por_ano["pct_horas_ar_seco"] * 100).round(2).tolist(),
            chart_type="line",
            border=True,
            help="Fração das horas medidas com umidade relativa de 30% ou menos. Diferença em pontos percentuais.",
        )
    with c4:
        st.metric(
            "Maior estiagem",
            f"{numero(estiagem)} dias",
            _delta(estiagem, media["maior_estiagem"] if comparar else None),
            delta_color="inverse",
            delta_description=descricao,
            chart_data=por_ano["maior_estiagem"].tolist(),
            chart_type="bar",
            border=True,
            help="Maior sequência de dias consecutivos com chuva abaixo de 1 mm "
            f"({periodo_estiagem}). Dia sem dado interrompe a sequência.",
        )
    with c5:
        st.metric(
            "Hora mais seca",
            f"{hora}h" if hora is not None else "—",
            f"{percentual(pct_hora)} das horas" if hora is not None else None,
            delta_color="off",
            delta_arrow="off",
            border=True,
            help="Hora local em que a umidade fica em 30% ou menos com mais frequência no recorte "
            "(o número abaixo é a fração dessas horas com UR ≤ 30%). "
            "É a janela a evitar para esforço físico ao ar livre.",
        )
    return {
        "dias_seco": dias_seco, "dias_alerta": dias_alerta, "pct_horas": pct_horas, "estiagem": estiagem,
        "periodo_estiagem": periodo_estiagem, "hora": hora, "pct_hora": pct_hora, "media": media,
    }


# ====================================================================== página


def render(df_horario: pd.DataFrame, df_diario: pd.DataFrame) -> None:
    anos = sorted(int(a) for a in df_diario["ano"].unique())
    with st.sidebar:
        st.header("Painel do tempo seco")
        foco = st.selectbox(
            "Ano em foco",
            [TODOS] + anos[::-1],
            format_func=lambda a: "2014–2023 (média anual)" if a == TODOS else str(a),
            key="d2_foco",
            help="Escolha um ano para compará-lo com a média de 2014–2023.",
        )
        recorte = st.segmented_control(
            "Meses considerados", list(RECORTES), default="Ano inteiro", required=True, key="d2_recorte"
        )
        st.caption(
            "Níveis de umidade relativa baixa usados pela Defesa Civil: **atenção** 21–30% · "
            "**alerta** 12–20% · **emergência** abaixo de 12%."
        )

    meses = RECORTES[recorte]
    diario_meses = df_diario[df_diario["mes"].isin(meses)]
    horario_meses = df_horario[df_horario["mes"].isin(meses)]
    por_ano = ind.indicadores_por_ano(diario_meses, horario_meses)
    if foco == TODOS:
        diario, horario = diario_meses, horario_meses
    else:
        diario = diario_meses[diario_meses["ano"] == foco]
        horario = horario_meses[horario_meses["ano"] == foco]

    st.markdown("### Painel do tempo seco")
    st.caption(
        "Para equipes de vigilância em saúde ambiental e Defesa Civil do DF: quantos dias de ar seco esperar, "
        "em que meses e horários eles se concentram, e como o ano escolhido se compara aos demais."
    )
    if diario.empty or horario.empty:
        st.warning("Não há dados para o recorte escolhido.")
        return

    k = mostra_kpis(diario, horario, por_ano, foco, recorte)

    # ------------------------------------------------------------ leitura rápida
    mapa = ind.mapa_mes_hora(horario)
    mes_pior = mapa.groupby("mes")["pct"].mean().idxmax()
    rotulo_foco = "Na média de 2014–2023" if foco == TODOS else f"Em {foco}"
    frases = [
        f"{rotulo_foco}, **{numero(k['dias_seco'], 0 if foco != TODOS else 1)} dias** "
        f"{'por ano ' if foco == TODOS else ''}tiveram umidade mínima de 30% ou menos"
        + (
            f" (média do período: {numero(k['media']['dias_ar_seco'], 1)})."
            if foco != TODOS else "."
        ),
        f"**{MESES_LONGOS[mes_pior - 1].capitalize()}** é o mês com mais horas de ar seco no recorte; "
        + (f"o risco se concentra por volta das **{k['hora']}h** (hora local)." if k["hora"] is not None else ""),
        f"Maior estiagem: **{numero(k['estiagem'])} dias** seguidos com menos de 1 mm de chuva, {k['periodo_estiagem']}.",
    ]
    with st.container(border=True):
        st.markdown("**Leitura rápida**")
        for f in frases:
            st.markdown(f"- {f}")

    # ------------------------------------------------------------ gráficos
    col_a, col_b = st.columns([1.25, 1], gap="large")
    with col_a:
        with st.container(border=True):
            st.markdown("**Quando o ar fica seco** · % das horas com UR ≤ 30%, por mês e hora")
            st.altair_chart(grafico_mapa_mes_hora(mapa, meses), width="stretch",
                            alt="Mapa de calor da fração de horas com umidade até 30% por mês e hora local")
            st.caption("Quanto mais escuro, mais frequente o ar seco naquela hora do mês. "
                       "Use para definir janelas de restrição de atividades ao ar livre.")
    with col_b:
        with st.container(border=True):
            titulo_y = "Dias por ano (média)" if foco == TODOS else "Dias"
            st.markdown("**Quantos dias em cada nível** · pela UR mínima do dia")
            st.altair_chart(
                grafico_niveis_mes(ind.dias_por_nivel_mes(diario, 1 if foco != TODOS else len(por_ano)),
                                   meses, titulo_y),
                width="stretch",
                alt="Barras empilhadas de dias por nível de umidade baixa em cada mês",
            )
            st.caption("Atenção, alerta e emergência seguem as faixas de UR da Defesa Civil.")

    col_c, col_d = st.columns(2, gap="large")
    with col_c:
        with st.container(border=True):
            st.markdown("**Ano a ano** · dias com UR mínima ≤ 30%")
            st.altair_chart(grafico_anual(por_ano, foco), width="stretch",
                            alt="Barras de dias com ar seco por ano, com a média do período")
            st.caption(f"Linha cinza = média 2014–2023 ({numero(por_ano['dias_ar_seco'].mean(), 1)} dias). " + (
                "Ano em foco destacado em azul." if foco != TODOS else "Escolha um ano no painel lateral para destacá-lo."
            ))
    with col_d:
        with st.container(border=True):
            st.markdown("**Ciclo diário da umidade** · mediana e 10% das horas mais secas")
            st.altair_chart(grafico_ciclo(ind.ciclo_diario(horario)), width="stretch",
                            alt="Linhas da umidade relativa por hora local: mediana e percentil 10")
            st.caption("O P10 mostra o patamar das horas mais secas: quando ele cruza a linha de 30%, "
                       "um em cada dez registros daquela hora já está em atenção.")

    # ------------------------------------------------------------ metodologia e dados
    with st.expander("Como os indicadores são calculados", icon=":material/functions:"):
        st.markdown(
            f"""
| Indicador | Fórmula | Unidade |
|---|---|---|
| Dias com ar seco | nº de dias com UR mínima ≤ 30% ÷ nº de anos | dias/ano (ou dias, com um ano em foco) |
| Dias em alerta | nº de dias com UR mínima ≤ 20% ÷ nº de anos | dias/ano (ou dias) |
| Horas com UR ≤ 30% | horas com UR ≤ 30% ÷ horas com UR medida | % (diferença em p.p.) |
| Maior estiagem | maior sequência de dias consecutivos com chuva < 1 mm | dias |
| Hora mais seca do dia | hora local com a maior fração de horas com UR ≤ 30% | hora |

- Um dia só entra nas contagens diárias se tiver pelo menos 20 horas de umidade medida
  ({numero(int(diario['umidade_min'].isna().sum()))} dia(s) do recorte atual ficaram de fora).
- A comparação usa a média dos mesmos indicadores calculados ano a ano, com o mesmo recorte de meses.
- Horários em hora local de Brasília (UTC−3). Fonte: INMET, estação automática A001.
"""
        )
        tabela = por_ano.drop(columns=["estiagem_inicio", "estiagem_fim"]).rename(
            columns={
                "ano": "Ano", "dias_ar_seco": "Dias UR ≤ 30%", "dias_alerta": "Dias UR ≤ 20%",
                "pct_horas_ar_seco": "% horas UR ≤ 30%", "maior_estiagem": "Maior estiagem (dias)",
                "chuva_total": "Chuva (mm)", "dias_validos": "Dias válidos",
            }
        )
        st.dataframe(
            tabela, hide_index=True, width="stretch",
            column_config={
                "Ano": st.column_config.NumberColumn(format="plain"),
                "% horas UR ≤ 30%": st.column_config.NumberColumn(format="percent"),
                "Chuva (mm)": st.column_config.NumberColumn(format="localized"),
            },
        )
        st.download_button(
            "Baixar indicadores por ano (CSV)",
            tabela.to_csv(index=False).encode("utf-8"),
            file_name="indicadores_tempo_seco_por_ano.csv",
            mime="text/csv",
            icon=":material/download:",
        )
