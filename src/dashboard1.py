# [IA] Claude Code (Claude Opus 5.5) – Dashboard 1: widgets, heatmap de correlação, histogramas e comparação
"""Dashboard 1 — Laboratório de distribuição e correlação.

Para quem explora o dado: escolher variáveis, cortar intervalos e ver como correlação e distribuição mudam.
"""

import altair as alt
import pandas as pd
import streamlit as st

from src import estatisticas as est
from src.formatacao import (
    COR_PRINCIPAL,
    COR_REFERENCIA,
    DIVERGENTE,
    ESTACOES,
    em_portugues,
    numero,
    percentual,
)
from src.variaveis import GRANULARIDADES, PADRAO, por_coluna

ALTURA_HIST = 210


# ====================================================================== gráficos


def grafico_heatmap(corr: pd.DataFrame, rotulos: dict[str, str], metodo: str) -> alt.Chart:
    dados = est.correlacao_longa(corr)
    dados["nome_linha"] = dados["linha"].map(rotulos)
    dados["nome_coluna"] = dados["coluna"].map(rotulos)
    dados["texto"] = dados["r"].map(lambda r: "—" if pd.isna(r) else numero(r, 2))
    dados["forca"] = dados["r"].map(est.forca_correlacao)
    ordem = [rotulos[c] for c in corr.columns]
    simbolo = "r" if metodo == "pearson" else "ρ"

    base = alt.Chart(dados).encode(
        x=alt.X("nome_coluna:N", sort=ordem, title=None, axis=alt.Axis(labelAngle=-30, labelLimit=140)),
        y=alt.Y("nome_linha:N", sort=ordem, title=None, axis=alt.Axis(labelLimit=160)),
    )
    celulas = base.mark_rect(cornerRadius=3, stroke="white", strokeWidth=2).encode(
        color=alt.Color(
            "r:Q",
            scale=alt.Scale(domain=[-1, 0, 1], range=DIVERGENTE),
            legend=alt.Legend(title=simbolo, orient="right", gradientLength=160),
        ),
        tooltip=[
            alt.Tooltip("nome_linha:N", title="Variável"),
            alt.Tooltip("nome_coluna:N", title="com"),
            alt.Tooltip("texto:N", title=simbolo),
            alt.Tooltip("forca:N", title="Força"),
        ],
    )
    textos = base.mark_text(fontSize=13, fontWeight=600).encode(
        text="texto:N",
        color=alt.condition("abs(datum.r) > 0.55", alt.value("white"), alt.value("#0b0b0b")),
    )
    altura = max(56 * len(ordem), 140)
    return em_portugues((celulas + textos).properties(height=altura))


def grafico_histograma(serie: pd.Series, nome: str, unidade: str, casas: int, bins: int, log: bool) -> alt.Chart:
    tabela = est.histograma(serie, bins)
    mediana = serie.median()
    escala_y = alt.Scale(type="symlog") if log else alt.Scale()
    barras = (
        alt.Chart(tabela)
        .mark_bar(color=COR_PRINCIPAL, binSpacing=1, cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X("inicio:Q", bin="binned", title=unidade, scale=alt.Scale(zero=False, nice=False)),
            x2="fim:Q",
            y=alt.Y("contagem:Q", title="Registros", scale=escala_y),
            tooltip=[
                alt.Tooltip("inicio:Q", title=f"De ({unidade})", format=f",.{casas}f"),
                alt.Tooltip("fim:Q", title=f"Até ({unidade})", format=f",.{casas}f"),
                alt.Tooltip("contagem:Q", title="Registros", format=","),
                alt.Tooltip("pct:Q", title="% do filtro", format=".1%"),
            ],
        )
    )
    regra = (
        alt.Chart(pd.DataFrame({"mediana": [mediana]}))
        .mark_rule(color=COR_REFERENCIA, strokeWidth=2)
        .encode(x="mediana:Q", tooltip=[alt.Tooltip("mediana:Q", title="Mediana", format=f",.{casas}f")])
    )
    return em_portugues((barras + regra).properties(height=ALTURA_HIST, title=alt.Title(nome, anchor="start")))


def grafico_densidade(df: pd.DataFrame, x, y) -> alt.Chart:
    tabela = est.densidade_2d(df, x.coluna, y.coluna, bins=35)
    return em_portugues(
        alt.Chart(tabela)
        .mark_rect()
        .encode(
            x=alt.X("x0:Q", bin="binned", title=x.rotulo, scale=alt.Scale(zero=False, nice=False)),
            x2="x1:Q",
            y=alt.Y("y0:Q", bin="binned", title=y.rotulo, scale=alt.Scale(zero=False, nice=False)),
            y2="y1:Q",
            color=alt.Color(
                "contagem:Q",
                scale=alt.Scale(scheme="blues", type="log"),
                legend=alt.Legend(title="Registros", gradientLength=140),
            ),
            tooltip=[
                alt.Tooltip("x0:Q", title=f"{x.nome} de", format=",.1f"),
                alt.Tooltip("x1:Q", title="até", format=",.1f"),
                alt.Tooltip("y0:Q", title=f"{y.nome} de", format=",.1f"),
                alt.Tooltip("y1:Q", title="até", format=",.1f"),
                alt.Tooltip("contagem:Q", title="Registros", format=","),
            ],
        )
        .properties(height=320)
    )


def grafico_boxplot(df: pd.DataFrame, var) -> alt.Chart:
    resumo = est.resumo_boxplot(df, var.coluna, "estacao", ESTACOES)
    base = alt.Chart(resumo).encode(y=alt.Y("estacao:N", sort=ESTACOES, title=None))
    dica = [
        alt.Tooltip("estacao:N", title="Estação"),
        alt.Tooltip("mediana:Q", title="Mediana", format=",.1f"),
        alt.Tooltip("q1:Q", title="Q1", format=",.1f"),
        alt.Tooltip("q3:Q", title="Q3", format=",.1f"),
        alt.Tooltip("outliers:Q", title="Outliers (IQR)", format=","),
        alt.Tooltip("n:Q", title="Registros", format=","),
    ]
    bigodes = base.mark_rule(color=COR_REFERENCIA).encode(
        x=alt.X("bigode_inf:Q", title=var.rotulo, scale=alt.Scale(zero=False)), x2="bigode_sup:Q", tooltip=dica
    )
    caixas = base.mark_bar(size=22, color=COR_PRINCIPAL, opacity=0.85, cornerRadius=3).encode(
        x="q1:Q", x2="q3:Q", tooltip=dica
    )
    medianas = base.mark_tick(color="white", thickness=2, size=22).encode(x="mediana:Q", tooltip=dica)
    return em_portugues((bigodes + caixas + medianas).properties(height=240))


# ====================================================================== textos de leitura


def leitura_correlacoes(corr: pd.DataFrame, corr_alt: pd.DataFrame, rotulos: dict[str, str], metodo: str) -> list[str]:
    """Frases curtas sobre os pares mais fortes e onde Pearson e Spearman divergem."""
    pares = est.pares_ordenados(corr)
    frases = []
    for _, p in pares.head(3).iterrows():
        if pd.isna(p["r"]):
            continue
        sentido = "sobem juntas" if p["r"] > 0 else "andam em sentidos opostos"
        if p["forca"] in ("desprezível", "fraca"):
            sentido = "quase não se relacionam (linearmente)" if metodo == "pearson" else "quase não se relacionam"
        frases.append(
            f"**{rotulos[p['a']]} × {rotulos[p['b']]}**: {numero(p['r'], 2)} ({p['forca']}) — {sentido}."
        )
    # Diferença grande entre Pearson e Spearman = relação não linear ou puxada por extremos
    outro = "Spearman" if metodo == "pearson" else "Pearson"
    divergentes = []
    for _, p in pares.iterrows():
        r2 = corr_alt.loc[p["a"], p["b"]]
        if pd.notna(p["r"]) and pd.notna(r2) and abs(p["r"] - r2) >= 0.15:
            divergentes.append(f"{rotulos[p['a']]} × {rotulos[p['b']]} ({outro}: {numero(r2, 2)})")
    if divergentes:
        frases.append(
            f"Pearson e Spearman divergem em: {'; '.join(divergentes[:3])}. "
            "Isso indica relação não linear ou influência de valores extremos."
        )
    return frases


def tabela_descritiva(desc: pd.DataFrame, catalogo: dict) -> pd.DataFrame:
    tabela = desc.copy()
    tabela.insert(0, "Variável", tabela.pop("variavel").map(lambda c: catalogo[c].rotulo))
    tabela = tabela.rename(
        columns={
            "n": "N", "ausentes": "Ausentes", "media": "Média", "mediana": "Mediana", "desvio": "Desvio-padrão",
            "minimo": "Mín.", "q1": "Q1", "q3": "Q3", "maximo": "Máx.", "assimetria": "Assimetria",
            "curtose": "Curtose", "forma": "Forma", "outliers": "Outliers (IQR)", "pct_outliers": "% outliers",
        }
    )
    return tabela.drop(columns=["iqr_nulo"], errors="ignore")


# ====================================================================== página


def _sidebar(df_horario: pd.DataFrame, df_diario: pd.DataFrame):
    with st.sidebar:
        st.header("Laboratório")
        granularidade = st.segmented_control(
            "Granularidade",
            list(GRANULARIDADES),
            default="Horária",
            required=True,
            key="d1_granularidade",
            help="Horária = medições originais do INMET. Diária = resumos de cada dia (máxima, mínima, total...).",
        )
        catalogo = por_coluna(granularidade)
        dados = df_horario if granularidade == "Horária" else df_diario

        variaveis = st.multiselect(
            "Variáveis avaliadas",
            options=list(catalogo),
            default=PADRAO[granularidade],
            format_func=lambda c: catalogo[c].rotulo,
            key=f"d1_variaveis_{granularidade}",
            help="Entram no heatmap, nos histogramas e na tabela de estatísticas.",
        )

        st.subheader("Recorte", divider="gray")
        anos = sorted(dados["ano"].unique())
        ano_ini, ano_fim = st.slider(
            "Anos", min_value=int(anos[0]), max_value=int(anos[-1]), value=(int(anos[0]), int(anos[-1])), key="d1_anos"
        )
        estacoes = st.pills(
            "Estações do ano", ESTACOES, selection_mode="multi", default=ESTACOES, key="d1_estacoes"
        )

        st.subheader("Excluir valores", divider="gray")
        var_corte = st.selectbox(
            "Variável do intervalo",
            options=list(catalogo),
            format_func=lambda c: catalogo[c].rotulo,
            index=list(catalogo).index(variaveis[0]) if variaveis else 0,
            key=f"d1_var_corte_{granularidade}",
            help="Só os registros dentro do intervalo escolhido entram na avaliação.",
        )
        v = catalogo[var_corte]
        serie = dados[var_corte].dropna()
        passo = 1.0 if v.casas == 0 else 0.1
        minimo, maximo = float(serie.min()), float(serie.max())
        intervalo = st.slider(
            f"Intervalo de {v.nome.lower()} ({v.unidade})",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            format="%.0f" if v.casas == 0 else "%.1f",
            key=f"d1_intervalo_{granularidade}_{var_corte}",
        )

        st.subheader("Exibição", divider="gray")
        metodo = st.segmented_control(
            "Correlação",
            ["pearson", "spearman"],
            default="pearson",
            required=True,
            format_func=lambda m: {"pearson": "Pearson", "spearman": "Spearman"}[m],
            key="d1_metodo",
            help="Pearson mede relação linear (é o usado na EDA). Spearman usa postos: é robusto a extremos "
            "e capta relações monotônicas não lineares.",
        )
        bins = st.slider("Faixas dos histogramas", 10, 60, 30, step=5, key="d1_bins")
        log = st.toggle(
            "Eixo de contagem em escala log",
            value=False,
            key="d1_log",
            help="Útil para variáveis muito concentradas, como a chuva (a maioria das horas tem 0 mm).",
        )
    return granularidade, catalogo, dados, variaveis, (ano_ini, ano_fim), estacoes, var_corte, intervalo, metodo, bins, log


def render(df_horario: pd.DataFrame, df_diario: pd.DataFrame) -> None:
    (granularidade, catalogo, dados, variaveis, (ano_ini, ano_fim), estacoes, var_corte, intervalo,
     metodo, bins, log) = _sidebar(df_horario, df_diario)

    st.markdown("### Laboratório de distribuição e correlação")
    st.caption(
        "Explore como as variáveis do clima de Brasília se distribuem e se relacionam. "
        "Use o painel lateral para escolher variáveis, recortar o período e excluir valores."
    )

    # ------------------------------------------------------------ aplica filtros
    filtro = dados["ano"].between(ano_ini, ano_fim) & dados["estacao"].isin(estacoes or [])
    dentro_intervalo = dados[var_corte].between(*intervalo)
    filtrado = dados[filtro & dentro_intervalo]
    unidade_registro = "horas" if granularidade == "Horária" else "dias"

    with st.container(horizontal=True):
        st.metric(
            f"Registros avaliados ({unidade_registro})",
            numero(len(filtrado)),
            help="Registros que passam por todos os filtros do painel lateral.",
            border=True,
        )
        st.metric(
            "Fração da base",
            percentual(len(filtrado) / len(dados)),
            help=f"Em relação aos {numero(len(dados))} registros da granularidade {granularidade.lower()}.",
            border=True,
        )
        st.metric(
            "Excluídos pelo intervalo",
            numero(int((filtro & ~dentro_intervalo).sum())),
            help=f"Registros do período/estações escolhidos com {catalogo[var_corte].nome.lower()} fora do intervalo "
            "(inclui registros sem leitura dessa variável).",
            border=True,
        )
        st.metric("Período", f"{ano_ini}–{ano_fim}" if ano_ini != ano_fim else str(ano_ini), border=True)

    if not estacoes:
        st.warning("Selecione pelo menos uma estação do ano no painel lateral.")
        return
    if filtrado.empty:
        st.warning("Nenhum registro atende aos filtros. Amplie o intervalo ou o período.")
        return
    if not variaveis:
        st.info("Selecione pelo menos uma variável no painel lateral para começar.")
        return

    rotulos = {c: catalogo[c].nome for c in variaveis}
    constantes = [rotulos[c] for c in variaveis if filtrado[c].nunique(dropna=True) <= 1]

    # ------------------------------------------------------------ correlação
    st.markdown("#### Correlação")
    col_mapa, col_leitura = st.columns([1.35, 1], gap="large")
    with col_mapa:
        if len(variaveis) < 2:
            st.info("Selecione pelo menos duas variáveis para calcular a correlação.")
        elif len(filtrado) < 3:
            st.warning("São necessários pelo menos 3 registros para calcular a correlação.")
        else:
            corr = est.matriz_correlacao(filtrado, variaveis, metodo)
            st.altair_chart(
                grafico_heatmap(corr, rotulos, metodo),
                width="stretch",
                alt=f"Heatmap da correlação de {metodo.title()} entre as variáveis selecionadas",
            )
    with col_leitura:
        if len(variaveis) >= 2 and len(filtrado) >= 3:
            outro = "spearman" if metodo == "pearson" else "pearson"
            corr_alt = est.matriz_correlacao(filtrado, variaveis, outro)
            with st.container(border=True):
                st.markdown("**Leitura rápida**")
                for frase in leitura_correlacoes(corr, corr_alt, rotulos, metodo):
                    st.markdown(f"- {frase}")
                if constantes:
                    st.markdown(
                        f"- {', '.join(constantes)} ficou constante no recorte: a correlação fica indefinida (—)."
                    )
            st.caption(
                "Escala usada: |r| < 0,1 desprezível · < 0,3 fraca · < 0,5 moderada · < 0,7 forte · ≥ 0,7 muito forte. "
                "Correlação descreve associação, não causa."
            )

    # ------------------------------------------------------------ distribuição
    st.markdown("#### Distribuição")
    desc = est.descritivas(filtrado, variaveis)
    n_col = 2 if len(variaveis) <= 4 else 3
    colunas = st.columns(n_col, gap="medium")
    for i, col in enumerate(variaveis):
        v = catalogo[col]
        linha = desc.set_index("variavel").loc[col]
        with colunas[i % n_col]:
            if linha["n"] == 0:
                st.info(f"{v.nome}: sem leituras válidas no recorte.")
                continue
            st.altair_chart(
                grafico_histograma(filtrado[col], v.nome, v.unidade, v.casas, bins, log),
                width="stretch",
                alt=f"Histograma de {v.nome}",
            )
            st.caption(
                f"Média {numero(linha['media'], v.casas)} · mediana {numero(linha['mediana'], v.casas)} {v.unidade} · "
                f"assimetria {numero(linha['assimetria'], 2)} ({linha['forma']})"
            )
    st.caption("Linha cinza = mediana. Passe o mouse nas barras para ver a faixa e a contagem.")

    # ------------------------------------------------------------ estatísticas e outliers
    with st.container(border=True):
        st.markdown("**Estatísticas descritivas e outliers (regra de 1,5 × IQR)**")
        st.dataframe(
            tabela_descritiva(desc, catalogo),
            hide_index=True,
            width="stretch",
            column_config={
                c: st.column_config.NumberColumn(format="%.2f")
                for c in ["Média", "Mediana", "Desvio-padrão", "Mín.", "Q1", "Q3", "Máx.", "Assimetria", "Curtose"]
            }
            | {
                "% outliers": st.column_config.NumberColumn(format="percent"),
                "N": st.column_config.NumberColumn(format="localized"),
                "Outliers (IQR)": st.column_config.NumberColumn(format="localized"),
            },
        )
        iqr_nulo = desc["iqr_nulo"].eq(True) if "iqr_nulo" in desc else pd.Series(False, index=desc.index)
        avisos_iqr = [catalogo[c].nome for c in desc.loc[iqr_nulo, "variavel"]]
        if avisos_iqr:
            st.caption(
                f"Atenção: em {', '.join(avisos_iqr)} o Q1 é igual ao Q3, então o IQR é zero e qualquer valor diferente "
                "da mediana vira \"outlier\". Na chuva, isso só marca as horas em que choveu — não é erro de medição "
                "(mesma conclusão da EDA). Como na EDA, nenhum extremo é removido automaticamente."
            )
        else:
            st.caption("Outliers são apenas sinalizados; como na EDA, valores extremos de clima podem ser reais.")

    # ------------------------------------------------------------ comparação entre duas variáveis
    st.markdown("#### Comparação entre variáveis")
    opcoes = list(catalogo)
    padrao_x = variaveis[0]
    padrao_y = variaveis[1] if len(variaveis) > 1 else opcoes[1 if opcoes[0] == padrao_x else 0]
    c1, c2 = st.columns(2)
    x_col = c1.selectbox(
        "Eixo X", opcoes, index=opcoes.index(padrao_x), format_func=lambda c: catalogo[c].rotulo,
        key=f"d1_x_{granularidade}",
    )
    y_col = c2.selectbox(
        "Eixo Y", opcoes, index=opcoes.index(padrao_y), format_func=lambda c: catalogo[c].rotulo,
        key=f"d1_y_{granularidade}",
    )
    x, y = catalogo[x_col], catalogo[y_col]
    col_disp, col_box = st.columns([1.3, 1], gap="large")
    with col_disp:
        if x_col == y_col:
            st.info("Escolha duas variáveis diferentes para comparar.")
        else:
            st.altair_chart(grafico_densidade(filtrado, x, y), width="stretch", alt=f"Densidade de {x.nome} × {y.nome}")
            par = filtrado[[x_col, y_col]].dropna()
            if len(par) >= 3 and par[x_col].nunique() > 1 and par[y_col].nunique() > 1:
                r_p = par[x_col].corr(par[y_col])
                r_s = par[x_col].corr(par[y_col], method="spearman")
                st.caption(
                    f"Cada célula conta quantos registros caem naquela combinação (cor em escala log). "
                    f"Pearson {numero(r_p, 2)} · Spearman {numero(r_s, 2)} · {numero(len(par))} pares válidos."
                )
    with col_box:
        st.altair_chart(grafico_boxplot(filtrado, y), width="stretch", alt=f"Boxplot de {y.nome} por estação")
        st.caption(f"{y.nome} por estação: caixa = Q1 a Q3, traço branco = mediana, linha = bigodes de 1,5 × IQR.")

    with st.expander("Sobre os dados deste laboratório"):
        st.markdown(
            f"""
- Fonte: INMET, estação automática A001 (Brasília), dados horários de 2014 a 2023, em **hora local (UTC−3)**.
- Tratamento da EDA: o código `-9999` (sem leitura) virou ausente; nenhum outlier foi removido.
- Correlação calculada par a par, ignorando registros ausentes em cada par.
- Na granularidade diária, cada resumo só é calculado se o dia tiver pelo menos 20 horas medidas.
- Recorte atual: {numero(len(filtrado))} {unidade_registro}.
"""
        )
