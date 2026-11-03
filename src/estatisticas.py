# [IA] Claude Code (Claude Opus 5.5) – funções estatísticas do Dashboard 1 (sem Streamlit, testáveis)
"""Cálculos do Dashboard 1: descritivas, assimetria, outliers (IQR), correlação e agregações para gráficos.

Tudo aqui recebe e devolve pandas, sem depender do Streamlit, para poder ser testado em tests/.
Os gráficos recebem dados já agregados (contagens por faixa), e não as ~87 mil linhas horárias.
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ descritivas


def classifica_assimetria(assimetria: float) -> str:
    """Regra de bolso (Bulmer): |g1| < 0,5 simétrica; 0,5–1 moderada; > 1 forte."""
    if pd.isna(assimetria):
        return "indefinida"
    lado = "à direita" if assimetria > 0 else "à esquerda"
    if abs(assimetria) < 0.5:
        return "aprox. simétrica"
    if abs(assimetria) <= 1:
        return f"moderada {lado}"
    return f"forte {lado}"


def limites_iqr(serie: pd.Series, k: float = 1.5) -> tuple[float, float]:
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def descritivas(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Uma linha por variável com as estatísticas usadas na tabela do Dashboard 1."""
    linhas = []
    for col in colunas:
        s = df[col].dropna()
        if s.empty:
            linhas.append({"variavel": col, "n": 0, "ausentes": int(df[col].isna().sum())})
            continue
        q1, q3 = s.quantile([0.25, 0.75])
        lim_inf, lim_sup = limites_iqr(s)
        n_out = int(((s < lim_inf) | (s > lim_sup)).sum())
        assim = s.skew() if s.nunique() > 1 else np.nan
        linhas.append(
            {
                "variavel": col,
                "n": int(s.size),
                "ausentes": int(df[col].isna().sum()),
                "media": s.mean(),
                "mediana": s.median(),
                "desvio": s.std() if s.size > 1 else np.nan,
                "minimo": s.min(),
                "q1": q1,
                "q3": q3,
                "maximo": s.max(),
                "assimetria": assim,
                "curtose": s.kurt() if s.nunique() > 1 else np.nan,
                "forma": classifica_assimetria(assim),
                "outliers": n_out,
                "pct_outliers": n_out / s.size,
                # Ex.: precipitação horária, com Q1 = Q3 = 0: o IQR é nulo e qualquer chuva vira "outlier"
                "iqr_nulo": bool(q3 - q1 == 0),
            }
        )
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ correlação


def matriz_correlacao(df: pd.DataFrame, colunas: list[str], metodo: str = "pearson") -> pd.DataFrame:
    """Correlação par a par (ignora NaN par a par). Variável constante → NaN na linha/coluna dela."""
    dados = df[colunas]
    corr = dados.corr(method=metodo)
    constantes = [c for c in colunas if dados[c].nunique(dropna=True) <= 1]
    if constantes:
        corr.loc[constantes, :] = np.nan
        corr.loc[:, constantes] = np.nan
    return corr


def correlacao_longa(corr: pd.DataFrame) -> pd.DataFrame:
    """Triângulo inferior (com a diagonal) em formato longo, para o heatmap."""
    colunas = list(corr.columns)
    linhas = [
        {"linha": y, "coluna": x, "r": corr.loc[y, x]}
        for i, y in enumerate(colunas)
        for x in colunas[: i + 1]
    ]
    return pd.DataFrame(linhas)


def forca_correlacao(r: float) -> str:
    """Faixas usuais de interpretação do |r| (convenção de Cohen, adaptada)."""
    if pd.isna(r):
        return "indefinida"
    a = abs(r)
    if a < 0.1:
        return "desprezível"
    if a < 0.3:
        return "fraca"
    if a < 0.5:
        return "moderada"
    if a < 0.7:
        return "forte"
    return "muito forte"


def pares_ordenados(corr: pd.DataFrame) -> pd.DataFrame:
    """Pares distintos (sem diagonal) ordenados do |r| maior para o menor; NaN vai para o fim."""
    colunas = list(corr.columns)
    pares = [
        {"a": a, "b": b, "r": corr.loc[a, b]}
        for i, a in enumerate(colunas)
        for b in colunas[i + 1 :]
    ]
    if not pares:
        return pd.DataFrame(columns=["a", "b", "r", "abs_r", "forca"])
    tabela = pd.DataFrame(pares)
    tabela["abs_r"] = tabela["r"].abs()
    tabela["forca"] = tabela["r"].map(forca_correlacao)
    return tabela.sort_values("abs_r", ascending=False, na_position="last").reset_index(drop=True)


# ------------------------------------------------------------------ agregações para gráficos


def histograma(serie: pd.Series, bins: int = 30, inteiro: bool = False) -> pd.DataFrame:
    """Contagens por faixa (início, fim, contagem, % do total).

    Com inteiro=True (ex.: umidade, medida em % inteiros), as faixas têm largura inteira e começam em x,5,
    para cada valor cair sempre no mesmo número de faixas — evita o "pente" de barras altas e baixas.
    """
    s = serie.dropna()
    if s.empty:
        return pd.DataFrame(columns=["inicio", "fim", "contagem", "pct"])
    minimo, maximo = s.min(), s.max()
    if minimo == maximo:  # variável constante: uma barra só, com largura simbólica
        bordas = np.array([minimo - 0.5, maximo + 0.5])
        contagens = np.array([s.size])
    elif inteiro:
        largura = max(1, int(np.ceil((maximo - minimo + 1) / bins)))
        bordas = np.arange(minimo - 0.5, maximo + largura + 0.5, largura)
        contagens, bordas = np.histogram(s, bins=bordas)
    else:
        contagens, bordas = np.histogram(s, bins=bins)
    tabela = pd.DataFrame({"inicio": bordas[:-1], "fim": bordas[1:], "contagem": contagens})
    tabela["pct"] = tabela["contagem"] / tabela["contagem"].sum()
    return tabela


def densidade_2d(df: pd.DataFrame, x: str, y: str, bins: int = 30) -> pd.DataFrame:
    """Contagem de registros em uma grade x × y (substitui o gráfico de dispersão de 87 mil pontos)."""
    dados = df[[x, y]].dropna()
    if dados.empty:
        return pd.DataFrame(columns=["x0", "x1", "y0", "y1", "contagem"])
    contagens, bx, by = np.histogram2d(dados[x], dados[y], bins=bins)
    ix, iy = np.nonzero(contagens)
    return pd.DataFrame(
        {
            "x0": bx[ix],
            "x1": bx[ix + 1],
            "y0": by[iy],
            "y1": by[iy + 1],
            "contagem": contagens[ix, iy].astype(int),
        }
    )


def resumo_boxplot(df: pd.DataFrame, valor: str, grupo: str, ordem: list[str]) -> pd.DataFrame:
    """Quartis, bigodes (1,5 × IQR, limitados aos dados) e nº de outliers por grupo."""
    linhas = []
    for nome in ordem:
        s = df.loc[df[grupo] == nome, valor].dropna()
        if s.empty:
            continue
        q1, mediana, q3 = s.quantile([0.25, 0.5, 0.75])
        lim_inf, lim_sup = limites_iqr(s)
        dentro = s[(s >= lim_inf) & (s <= lim_sup)]
        linhas.append(
            {
                grupo: nome,
                "q1": q1,
                "mediana": mediana,
                "q3": q3,
                "bigode_inf": dentro.min(),
                "bigode_sup": dentro.max(),
                "outliers": int(((s < lim_inf) | (s > lim_sup)).sum()),
                "n": int(s.size),
            }
        )
    return pd.DataFrame(linhas)
