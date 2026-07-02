"""Testes basicos para o modulo de features."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from features import (
    is_valid_location,
    calculate_distance,
    extract_defensive_line_height,
    extract_pass_length_profile,
)


def test_is_valid_location_with_list():
    """Testa validacao de localizacao com lista."""
    assert is_valid_location([10.0, 20.0]) == True
    assert is_valid_location([10.0]) == False
    assert is_valid_location([]) == False
    assert is_valid_location(None) == False


def test_is_valid_location_with_numpy():
    """Testa validacao de localizacao com numpy array."""
    assert is_valid_location(np.array([10.0, 20.0])) == True
    assert is_valid_location(np.array([10.0])) == False


def test_calculate_distance():
    """Testa calculo de distancia."""
    assert calculate_distance([0, 0], [3, 4]) == 5.0
    assert calculate_distance([0, 0], [0, 0]) == 0.0
    assert calculate_distance(None, [1, 1]) == 0.0


def test_extract_defensive_line_height_empty():
    """Testa extracao de linha defensiva com dados vazios."""
    events = pd.DataFrame({
        "team": ["Brazil"],
        "type": ["Pass"],
        "location": [[50.0, 40.0]],
    })
    result = extract_defensive_line_height(events, "Brazil")
    assert result == 40.0  # valor default


def test_extract_defensive_line_height_with_data():
    """Testa extracao de linha defensiva com dados reais."""
    events = pd.DataFrame({
        "team": ["Brazil", "Brazil", "Brazil"],
        "type": ["Tackle", "Interception", "Block"],
        "location": [np.array([30.0, 40.0]), np.array([40.0, 40.0]), np.array([35.0, 40.0])],
    })
    result = extract_defensive_line_height(events, "Brazil")
    assert result == 35.0  # media de 30, 40, 35


def test_extract_pass_length_profile():
    """Testa perfil de comprimento de passes."""
    # Criar passes de diferentes tamanhos
    events = pd.DataFrame({
        "team": ["Brazil"] * 3,
        "type": ["Pass"] * 3,
        "location": [
            np.array([0.0, 0.0]),
            np.array([0.0, 0.0]),
            np.array([0.0, 0.0]),
        ],
        "pass_end_location": [
            np.array([10.0, 0.0]),  # curto (10m)
            np.array([20.0, 0.0]),  # medio (20m)
            np.array([40.0, 0.0]),  # longo (40m)
        ],
    })

    short_pct, long_pct = extract_pass_length_profile(events, "Brazil")

    assert short_pct == pytest.approx(1/3, rel=0.01)  # 1 de 3 curto
    assert long_pct == pytest.approx(1/3, rel=0.01)   # 1 de 3 longo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
