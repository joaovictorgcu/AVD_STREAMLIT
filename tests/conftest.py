# [IA] Claude Code (Claude Opus 5.5) – configuração comum dos testes
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.data_loader import agrega_diario  # noqa: E402


@pytest.fixture(scope="session")
def horario() -> pd.DataFrame:
    return pd.read_csv(RAIZ / "data" / "clean" / "dataset.csv", parse_dates=["data_hora", "data"])


@pytest.fixture(scope="session")
def diario(horario) -> pd.DataFrame:
    return agrega_diario(horario)
