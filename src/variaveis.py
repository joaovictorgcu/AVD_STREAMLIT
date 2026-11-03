# [IA] Claude Code (Claude Opus 5.5) – catálogo das variáveis quantitativas (nomes, unidades e descrição)
"""Variáveis quantitativas avaliadas no Dashboard 1, por granularidade.

Horária = medições originais do INMET (mais o ponto de orvalho, derivado na EDA com downloads).
Diária = resumos por dia local, calculados em src/data_loader.agrega_diario.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Variavel:
    coluna: str
    nome: str
    unidade: str
    descricao: str
    casas: int = 1
    curto: str = ""  # nome curto para eixos apertados (heatmap)

    @property
    def rotulo(self) -> str:
        return f"{self.nome} ({self.unidade})"


HORARIAS = [
    Variavel("temperatura", "Temperatura", "°C", "Temperatura do ar (bulbo seco) na hora.", curto="Temp."),
    Variavel("umidade", "Umidade relativa", "%", "Umidade relativa do ar na hora.", 0, "Umidade"),
    Variavel("precipitacao", "Precipitação", "mm", "Chuva acumulada na hora.", curto="Chuva"),
    Variavel(
        "ponto_orvalho",
        "Ponto de orvalho",
        "°C",
        "Temperatura em que o ar saturaria (fórmula de Magnus). Mede o vapor d'água absoluto.",
        curto="Orvalho",
    ),
]

DIARIAS = [
    Variavel("temp_media", "Temperatura média", "°C", "Média das temperaturas horárias do dia.", curto="T média"),
    Variavel("temp_max", "Temperatura máxima", "°C", "Maior temperatura horária do dia.", curto="T máx."),
    Variavel("temp_min", "Temperatura mínima", "°C", "Menor temperatura horária do dia.", curto="T mín."),
    Variavel("amplitude_termica", "Amplitude térmica", "°C", "Máxima menos mínima do dia.", curto="Amplitude"),
    Variavel("umidade_media", "Umidade média", "%", "Média da umidade relativa no dia.", 0, "UR média"),
    Variavel("umidade_min", "Umidade mínima", "%", "Menor umidade relativa horária do dia.", 0, "UR mín."),
    Variavel("chuva_total", "Chuva do dia", "mm", "Soma da precipitação horária do dia.", curto="Chuva"),
    Variavel("orvalho_medio", "Ponto de orvalho médio", "°C", "Média do ponto de orvalho no dia.", curto="Orvalho"),
]

GRANULARIDADES = {"Horária": HORARIAS, "Diária": DIARIAS}

# Seleção inicial de cada granularidade (as que contam a história principal da EDA)
PADRAO = {
    "Horária": ["temperatura", "umidade", "precipitacao", "ponto_orvalho"],
    "Diária": ["temp_max", "amplitude_termica", "umidade_min", "chuva_total"],
}


def por_coluna(granularidade: str) -> dict[str, Variavel]:
    return {v.coluna: v for v in GRANULARIDADES[granularidade]}
