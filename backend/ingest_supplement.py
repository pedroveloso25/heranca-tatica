"""
Ingestao de dados suplementares para todas as selecoes.
Complementa os dados StatsBomb para Copas do Mundo sem cobertura completa.

Este modulo NAO calcula features taticas - apenas registra dados historicos
basicos (jogos, gols, fase alcancada) para contexto.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import requests

DATA_DIR = Path(__file__).parent / "data"
SUPPLEMENT_FILE = DATA_DIR / "supplement.json"

# API do football-data.org
API_BASE = "https://api.football-data.org/v4"

# Niveis de confiabilidade baseados no diagnostico StatsBomb
# Mapeamento por selecao e ano
STATSBOMB_COVERAGE = {
    "Brazil": {
        "1958": {"jogos": 2, "nivel": "parcial"},
        "1962": {"jogos": 1, "nivel": "parcial"},
        "1970": {"jogos": 6, "nivel": "completo"},
        "1974": {"jogos": 1, "nivel": "parcial"},
        "1986": {"jogos": 0, "nivel": "parcial"},
        "1990": {"jogos": 1, "nivel": "parcial"},
        "2018": {"jogos": 5, "nivel": "completo"},
        "2022": {"jogos": 5, "nivel": "completo"},
    },
    "Germany": {
        "1970": {"jogos": 6, "nivel": "completo"},
        "2018": {"jogos": 7, "nivel": "completo"},
        "2022": {"jogos": 3, "nivel": "completo"},
    },
    "Argentina": {
        "1970": {"jogos": 0, "nivel": "referencia"},
        "2018": {"jogos": 4, "nivel": "completo"},
        "2022": {"jogos": 7, "nivel": "completo"},
    },
    "France": {
        "1970": {"jogos": 0, "nivel": "referencia"},
        "2018": {"jogos": 7, "nivel": "completo"},
        "2022": {"jogos": 7, "nivel": "completo"},
    },
    "Italy": {
        "1970": {"jogos": 6, "nivel": "completo"},
        "2018": {"jogos": 0, "nivel": "referencia"},
        "2022": {"jogos": 0, "nivel": "referencia"},
    },
    "England": {
        "1970": {"jogos": 4, "nivel": "completo"},
        "2018": {"jogos": 7, "nivel": "completo"},
        "2022": {"jogos": 5, "nivel": "completo"},
    },
    "Spain": {
        "1970": {"jogos": 0, "nivel": "referencia"},
        "2018": {"jogos": 4, "nivel": "completo"},
        "2022": {"jogos": 4, "nivel": "completo"},
    },
    "Netherlands": {
        "1970": {"jogos": 0, "nivel": "referencia"},
        "2018": {"jogos": 0, "nivel": "referencia"},
        "2022": {"jogos": 5, "nivel": "completo"},
    },
    "Uruguay": {
        "1970": {"jogos": 4, "nivel": "completo"},
        "2018": {"jogos": 5, "nivel": "completo"},
        "2022": {"jogos": 4, "nivel": "completo"},
    },
}

# Copas ausentes do StatsBomb para todos = nivel "referencia"
COPAS_REFERENCIA = [
    "1930", "1934", "1938", "1950", "1954", "1966",
    "1978", "1982", "1994", "1998", "2002", "2006", "2010", "2014"
]


def get_confidence_level(team: str, year: str) -> str:
    """Retorna o nivel de confiabilidade para uma selecao em uma Copa."""
    if year in COPAS_REFERENCIA:
        return "referencia"

    team_coverage = STATSBOMB_COVERAGE.get(team, {})
    if year in team_coverage:
        return team_coverage[year]["nivel"]

    # Se a Copa tem dados StatsBomb mas a selecao nao esta mapeada,
    # verificar se e uma Copa com cobertura geral
    if year in ["2018", "2022"]:
        return "completo"  # Copas modernas tem cobertura completa
    elif year in ["1970"]:
        return "completo"  # Copa 1970 tem boa cobertura

    return "referencia"


# Dados historicos conhecidos de todas as selecoes em Copas do Mundo
# Fonte: FIFA, Wikipedia, documentacao publica
HISTORICAL_DATA = {
    "Brazil": {
        1930: {"jogos": 2, "gols_pro": 5, "gols_contra": 2, "resultado": "fase_grupos"},
        1934: {"jogos": 1, "gols_pro": 1, "gols_contra": 3, "resultado": "fase_grupos"},
        1938: {"jogos": 5, "gols_pro": 14, "gols_contra": 11, "resultado": "terceiro"},
        1950: {"jogos": 6, "gols_pro": 22, "gols_contra": 6, "resultado": "vice"},
        1954: {"jogos": 3, "gols_pro": 8, "gols_contra": 5, "resultado": "quartas"},
        1958: {"jogos": 6, "gols_pro": 16, "gols_contra": 4, "resultado": "campeao"},
        1962: {"jogos": 6, "gols_pro": 14, "gols_contra": 5, "resultado": "campeao"},
        1966: {"jogos": 3, "gols_pro": 4, "gols_contra": 6, "resultado": "fase_grupos"},
        1970: {"jogos": 6, "gols_pro": 19, "gols_contra": 7, "resultado": "campeao"},
        1974: {"jogos": 7, "gols_pro": 6, "gols_contra": 4, "resultado": "quartas"},
        1978: {"jogos": 7, "gols_pro": 10, "gols_contra": 3, "resultado": "terceiro"},
        1982: {"jogos": 5, "gols_pro": 15, "gols_contra": 6, "resultado": "oitavas"},
        1986: {"jogos": 5, "gols_pro": 10, "gols_contra": 1, "resultado": "quartas"},
        1990: {"jogos": 4, "gols_pro": 4, "gols_contra": 2, "resultado": "oitavas"},
        1994: {"jogos": 7, "gols_pro": 11, "gols_contra": 3, "resultado": "campeao"},
        1998: {"jogos": 7, "gols_pro": 14, "gols_contra": 10, "resultado": "vice"},
        2002: {"jogos": 7, "gols_pro": 18, "gols_contra": 4, "resultado": "campeao"},
        2006: {"jogos": 5, "gols_pro": 10, "gols_contra": 2, "resultado": "quartas"},
        2010: {"jogos": 5, "gols_pro": 9, "gols_contra": 4, "resultado": "quartas"},
        2014: {"jogos": 7, "gols_pro": 11, "gols_contra": 14, "resultado": "quartas"},
        2018: {"jogos": 5, "gols_pro": 8, "gols_contra": 3, "resultado": "quartas"},
        2022: {"jogos": 5, "gols_pro": 8, "gols_contra": 3, "resultado": "quartas"},
    },
    "Argentina": {
        1930: {"jogos": 5, "gols_pro": 18, "gols_contra": 9, "resultado": "vice"},
        1934: {"jogos": 1, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        1958: {"jogos": 3, "gols_pro": 5, "gols_contra": 10, "resultado": "fase_grupos"},
        1962: {"jogos": 3, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        1966: {"jogos": 4, "gols_pro": 4, "gols_contra": 2, "resultado": "quartas"},
        1974: {"jogos": 6, "gols_pro": 9, "gols_contra": 6, "resultado": "oitavas"},
        1978: {"jogos": 7, "gols_pro": 15, "gols_contra": 4, "resultado": "campeao"},
        1982: {"jogos": 5, "gols_pro": 8, "gols_contra": 7, "resultado": "oitavas"},
        1986: {"jogos": 7, "gols_pro": 14, "gols_contra": 5, "resultado": "campeao"},
        1990: {"jogos": 7, "gols_pro": 5, "gols_contra": 4, "resultado": "vice"},
        1994: {"jogos": 4, "gols_pro": 8, "gols_contra": 3, "resultado": "oitavas"},
        1998: {"jogos": 5, "gols_pro": 10, "gols_contra": 4, "resultado": "quartas"},
        2002: {"jogos": 3, "gols_pro": 2, "gols_contra": 2, "resultado": "fase_grupos"},
        2006: {"jogos": 5, "gols_pro": 11, "gols_contra": 3, "resultado": "quartas"},
        2010: {"jogos": 5, "gols_pro": 10, "gols_contra": 6, "resultado": "quartas"},
        2014: {"jogos": 7, "gols_pro": 8, "gols_contra": 4, "resultado": "vice"},
        2018: {"jogos": 4, "gols_pro": 6, "gols_contra": 9, "resultado": "oitavas"},
        2022: {"jogos": 7, "gols_pro": 15, "gols_contra": 8, "resultado": "campeao"},
    },
    "Germany": {
        1934: {"jogos": 4, "gols_pro": 11, "gols_contra": 8, "resultado": "terceiro"},
        1938: {"jogos": 2, "gols_pro": 3, "gols_contra": 5, "resultado": "fase_grupos"},
        1954: {"jogos": 6, "gols_pro": 25, "gols_contra": 14, "resultado": "campeao"},
        1958: {"jogos": 4, "gols_pro": 12, "gols_contra": 7, "resultado": "quartas"},
        1962: {"jogos": 4, "gols_pro": 4, "gols_contra": 2, "resultado": "quartas"},
        1966: {"jogos": 6, "gols_pro": 15, "gols_contra": 6, "resultado": "vice"},
        1970: {"jogos": 6, "gols_pro": 17, "gols_contra": 10, "resultado": "terceiro"},
        1974: {"jogos": 7, "gols_pro": 13, "gols_contra": 4, "resultado": "campeao"},
        1978: {"jogos": 6, "gols_pro": 10, "gols_contra": 5, "resultado": "oitavas"},
        1982: {"jogos": 7, "gols_pro": 12, "gols_contra": 10, "resultado": "vice"},
        1986: {"jogos": 7, "gols_pro": 8, "gols_contra": 7, "resultado": "vice"},
        1990: {"jogos": 7, "gols_pro": 15, "gols_contra": 5, "resultado": "campeao"},
        1994: {"jogos": 5, "gols_pro": 9, "gols_contra": 6, "resultado": "quartas"},
        1998: {"jogos": 5, "gols_pro": 8, "gols_contra": 6, "resultado": "quartas"},
        2002: {"jogos": 7, "gols_pro": 14, "gols_contra": 3, "resultado": "vice"},
        2006: {"jogos": 7, "gols_pro": 14, "gols_contra": 6, "resultado": "terceiro"},
        2010: {"jogos": 7, "gols_pro": 16, "gols_contra": 5, "resultado": "terceiro"},
        2014: {"jogos": 7, "gols_pro": 18, "gols_contra": 4, "resultado": "campeao"},
        2018: {"jogos": 3, "gols_pro": 2, "gols_contra": 4, "resultado": "fase_grupos"},
        2022: {"jogos": 3, "gols_pro": 6, "gols_contra": 5, "resultado": "fase_grupos"},
    },
    "France": {
        1930: {"jogos": 2, "gols_pro": 4, "gols_contra": 3, "resultado": "fase_grupos"},
        1934: {"jogos": 1, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        1938: {"jogos": 2, "gols_pro": 4, "gols_contra": 4, "resultado": "quartas"},
        1954: {"jogos": 2, "gols_pro": 3, "gols_contra": 8, "resultado": "fase_grupos"},
        1958: {"jogos": 6, "gols_pro": 23, "gols_contra": 15, "resultado": "terceiro"},
        1966: {"jogos": 3, "gols_pro": 2, "gols_contra": 5, "resultado": "fase_grupos"},
        1978: {"jogos": 3, "gols_pro": 5, "gols_contra": 5, "resultado": "fase_grupos"},
        1982: {"jogos": 7, "gols_pro": 16, "gols_contra": 12, "resultado": "quartas"},
        1986: {"jogos": 7, "gols_pro": 12, "gols_contra": 6, "resultado": "terceiro"},
        1998: {"jogos": 7, "gols_pro": 15, "gols_contra": 2, "resultado": "campeao"},
        2002: {"jogos": 3, "gols_pro": 0, "gols_contra": 3, "resultado": "fase_grupos"},
        2006: {"jogos": 7, "gols_pro": 9, "gols_contra": 3, "resultado": "vice"},
        2010: {"jogos": 3, "gols_pro": 1, "gols_contra": 4, "resultado": "fase_grupos"},
        2014: {"jogos": 5, "gols_pro": 10, "gols_contra": 3, "resultado": "quartas"},
        2018: {"jogos": 7, "gols_pro": 14, "gols_contra": 6, "resultado": "campeao"},
        2022: {"jogos": 7, "gols_pro": 16, "gols_contra": 8, "resultado": "vice"},
    },
    "Italy": {
        1934: {"jogos": 5, "gols_pro": 12, "gols_contra": 3, "resultado": "campeao"},
        1938: {"jogos": 4, "gols_pro": 11, "gols_contra": 5, "resultado": "campeao"},
        1950: {"jogos": 2, "gols_pro": 4, "gols_contra": 3, "resultado": "fase_grupos"},
        1954: {"jogos": 2, "gols_pro": 5, "gols_contra": 6, "resultado": "fase_grupos"},
        1962: {"jogos": 3, "gols_pro": 3, "gols_contra": 2, "resultado": "fase_grupos"},
        1966: {"jogos": 3, "gols_pro": 2, "gols_contra": 2, "resultado": "fase_grupos"},
        1970: {"jogos": 6, "gols_pro": 10, "gols_contra": 8, "resultado": "vice"},
        1974: {"jogos": 3, "gols_pro": 5, "gols_contra": 4, "resultado": "fase_grupos"},
        1978: {"jogos": 7, "gols_pro": 9, "gols_contra": 6, "resultado": "quartas"},
        1982: {"jogos": 7, "gols_pro": 12, "gols_contra": 6, "resultado": "campeao"},
        1986: {"jogos": 4, "gols_pro": 5, "gols_contra": 6, "resultado": "oitavas"},
        1990: {"jogos": 7, "gols_pro": 10, "gols_contra": 2, "resultado": "terceiro"},
        1994: {"jogos": 7, "gols_pro": 8, "gols_contra": 5, "resultado": "vice"},
        1998: {"jogos": 5, "gols_pro": 8, "gols_contra": 6, "resultado": "quartas"},
        2002: {"jogos": 4, "gols_pro": 5, "gols_contra": 3, "resultado": "oitavas"},
        2006: {"jogos": 7, "gols_pro": 12, "gols_contra": 2, "resultado": "campeao"},
        2010: {"jogos": 3, "gols_pro": 4, "gols_contra": 5, "resultado": "fase_grupos"},
        2014: {"jogos": 3, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
    },
    "England": {
        1950: {"jogos": 3, "gols_pro": 2, "gols_contra": 2, "resultado": "fase_grupos"},
        1954: {"jogos": 3, "gols_pro": 8, "gols_contra": 8, "resultado": "quartas"},
        1958: {"jogos": 4, "gols_pro": 4, "gols_contra": 5, "resultado": "fase_grupos"},
        1962: {"jogos": 4, "gols_pro": 5, "gols_contra": 6, "resultado": "quartas"},
        1966: {"jogos": 6, "gols_pro": 11, "gols_contra": 3, "resultado": "campeao"},
        1970: {"jogos": 4, "gols_pro": 4, "gols_contra": 4, "resultado": "quartas"},
        1982: {"jogos": 5, "gols_pro": 6, "gols_contra": 1, "resultado": "oitavas"},
        1986: {"jogos": 5, "gols_pro": 7, "gols_contra": 3, "resultado": "quartas"},
        1990: {"jogos": 7, "gols_pro": 8, "gols_contra": 6, "resultado": "quartas"},
        1998: {"jogos": 4, "gols_pro": 7, "gols_contra": 4, "resultado": "oitavas"},
        2002: {"jogos": 5, "gols_pro": 6, "gols_contra": 3, "resultado": "quartas"},
        2006: {"jogos": 5, "gols_pro": 6, "gols_contra": 2, "resultado": "quartas"},
        2010: {"jogos": 4, "gols_pro": 3, "gols_contra": 5, "resultado": "oitavas"},
        2014: {"jogos": 3, "gols_pro": 2, "gols_contra": 4, "resultado": "fase_grupos"},
        2018: {"jogos": 7, "gols_pro": 12, "gols_contra": 8, "resultado": "quartas"},
        2022: {"jogos": 5, "gols_pro": 13, "gols_contra": 4, "resultado": "quartas"},
    },
    "Spain": {
        1934: {"jogos": 3, "gols_pro": 4, "gols_contra": 3, "resultado": "quartas"},
        1950: {"jogos": 6, "gols_pro": 10, "gols_contra": 12, "resultado": "quartas"},
        1962: {"jogos": 3, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        1966: {"jogos": 3, "gols_pro": 4, "gols_contra": 5, "resultado": "fase_grupos"},
        1978: {"jogos": 3, "gols_pro": 2, "gols_contra": 5, "resultado": "fase_grupos"},
        1982: {"jogos": 5, "gols_pro": 4, "gols_contra": 5, "resultado": "oitavas"},
        1986: {"jogos": 5, "gols_pro": 11, "gols_contra": 4, "resultado": "quartas"},
        1990: {"jogos": 4, "gols_pro": 6, "gols_contra": 4, "resultado": "oitavas"},
        1994: {"jogos": 5, "gols_pro": 10, "gols_contra": 6, "resultado": "quartas"},
        1998: {"jogos": 4, "gols_pro": 8, "gols_contra": 4, "resultado": "fase_grupos"},
        2002: {"jogos": 5, "gols_pro": 10, "gols_contra": 5, "resultado": "quartas"},
        2006: {"jogos": 4, "gols_pro": 9, "gols_contra": 4, "resultado": "oitavas"},
        2010: {"jogos": 7, "gols_pro": 8, "gols_contra": 2, "resultado": "campeao"},
        2014: {"jogos": 3, "gols_pro": 4, "gols_contra": 7, "resultado": "fase_grupos"},
        2018: {"jogos": 4, "gols_pro": 7, "gols_contra": 6, "resultado": "oitavas"},
        2022: {"jogos": 4, "gols_pro": 9, "gols_contra": 3, "resultado": "oitavas"},
    },
    "Netherlands": {
        1934: {"jogos": 1, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        1938: {"jogos": 1, "gols_pro": 0, "gols_contra": 3, "resultado": "fase_grupos"},
        1974: {"jogos": 7, "gols_pro": 15, "gols_contra": 3, "resultado": "vice"},
        1978: {"jogos": 7, "gols_pro": 15, "gols_contra": 7, "resultado": "vice"},
        1990: {"jogos": 4, "gols_pro": 6, "gols_contra": 3, "resultado": "oitavas"},
        1994: {"jogos": 5, "gols_pro": 8, "gols_contra": 6, "resultado": "quartas"},
        1998: {"jogos": 7, "gols_pro": 13, "gols_contra": 7, "resultado": "quartas"},
        2006: {"jogos": 4, "gols_pro": 3, "gols_contra": 3, "resultado": "oitavas"},
        2010: {"jogos": 7, "gols_pro": 12, "gols_contra": 6, "resultado": "vice"},
        2014: {"jogos": 7, "gols_pro": 15, "gols_contra": 4, "resultado": "terceiro"},
        2022: {"jogos": 5, "gols_pro": 10, "gols_contra": 5, "resultado": "quartas"},
    },
    "Uruguay": {
        1930: {"jogos": 4, "gols_pro": 15, "gols_contra": 3, "resultado": "campeao"},
        1950: {"jogos": 4, "gols_pro": 15, "gols_contra": 5, "resultado": "campeao"},
        1954: {"jogos": 4, "gols_pro": 16, "gols_contra": 9, "resultado": "quartas"},
        1962: {"jogos": 3, "gols_pro": 4, "gols_contra": 6, "resultado": "fase_grupos"},
        1966: {"jogos": 4, "gols_pro": 2, "gols_contra": 5, "resultado": "quartas"},
        1970: {"jogos": 6, "gols_pro": 4, "gols_contra": 5, "resultado": "quartas"},
        1974: {"jogos": 3, "gols_pro": 1, "gols_contra": 6, "resultado": "fase_grupos"},
        1986: {"jogos": 4, "gols_pro": 2, "gols_contra": 8, "resultado": "oitavas"},
        1990: {"jogos": 4, "gols_pro": 2, "gols_contra": 3, "resultado": "oitavas"},
        2002: {"jogos": 3, "gols_pro": 4, "gols_contra": 5, "resultado": "fase_grupos"},
        2010: {"jogos": 7, "gols_pro": 11, "gols_contra": 5, "resultado": "quartas"},
        2014: {"jogos": 4, "gols_pro": 4, "gols_contra": 6, "resultado": "oitavas"},
        2018: {"jogos": 5, "gols_pro": 7, "gols_contra": 3, "resultado": "quartas"},
        2022: {"jogos": 4, "gols_pro": 3, "gols_contra": 3, "resultado": "fase_grupos"},
    },
    "Portugal": {
        1966: {"jogos": 6, "gols_pro": 17, "gols_contra": 8, "resultado": "terceiro"},
        1986: {"jogos": 3, "gols_pro": 2, "gols_contra": 4, "resultado": "fase_grupos"},
        2002: {"jogos": 3, "gols_pro": 6, "gols_contra": 4, "resultado": "fase_grupos"},
        2006: {"jogos": 7, "gols_pro": 7, "gols_contra": 5, "resultado": "quartas"},
        2010: {"jogos": 4, "gols_pro": 7, "gols_contra": 1, "resultado": "oitavas"},
        2014: {"jogos": 3, "gols_pro": 4, "gols_contra": 7, "resultado": "fase_grupos"},
        2018: {"jogos": 4, "gols_pro": 6, "gols_contra": 6, "resultado": "oitavas"},
        2022: {"jogos": 5, "gols_pro": 12, "gols_contra": 6, "resultado": "quartas"},
    },
    "Belgium": {
        1930: {"jogos": 2, "gols_pro": 0, "gols_contra": 4, "resultado": "fase_grupos"},
        1934: {"jogos": 1, "gols_pro": 2, "gols_contra": 5, "resultado": "fase_grupos"},
        1938: {"jogos": 1, "gols_pro": 1, "gols_contra": 3, "resultado": "fase_grupos"},
        1954: {"jogos": 2, "gols_pro": 5, "gols_contra": 5, "resultado": "fase_grupos"},
        1970: {"jogos": 3, "gols_pro": 4, "gols_contra": 5, "resultado": "fase_grupos"},
        1982: {"jogos": 5, "gols_pro": 3, "gols_contra": 5, "resultado": "oitavas"},
        1986: {"jogos": 7, "gols_pro": 12, "gols_contra": 8, "resultado": "quartas"},
        1990: {"jogos": 4, "gols_pro": 6, "gols_contra": 4, "resultado": "oitavas"},
        1994: {"jogos": 4, "gols_pro": 4, "gols_contra": 4, "resultado": "oitavas"},
        1998: {"jogos": 3, "gols_pro": 3, "gols_contra": 3, "resultado": "fase_grupos"},
        2002: {"jogos": 4, "gols_pro": 6, "gols_contra": 7, "resultado": "oitavas"},
        2014: {"jogos": 5, "gols_pro": 6, "gols_contra": 3, "resultado": "quartas"},
        2018: {"jogos": 7, "gols_pro": 16, "gols_contra": 6, "resultado": "terceiro"},
        2022: {"jogos": 3, "gols_pro": 1, "gols_contra": 2, "resultado": "fase_grupos"},
    },
    "Croatia": {
        1998: {"jogos": 7, "gols_pro": 11, "gols_contra": 5, "resultado": "terceiro"},
        2002: {"jogos": 3, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
        2006: {"jogos": 3, "gols_pro": 2, "gols_contra": 2, "resultado": "fase_grupos"},
        2014: {"jogos": 3, "gols_pro": 6, "gols_contra": 6, "resultado": "fase_grupos"},
        2018: {"jogos": 7, "gols_pro": 14, "gols_contra": 9, "resultado": "vice"},
        2022: {"jogos": 7, "gols_pro": 8, "gols_contra": 7, "resultado": "terceiro"},
    },
    "Mexico": {
        1930: {"jogos": 3, "gols_pro": 4, "gols_contra": 13, "resultado": "fase_grupos"},
        1950: {"jogos": 3, "gols_pro": 2, "gols_contra": 10, "resultado": "fase_grupos"},
        1954: {"jogos": 2, "gols_pro": 2, "gols_contra": 8, "resultado": "fase_grupos"},
        1958: {"jogos": 3, "gols_pro": 1, "gols_contra": 8, "resultado": "fase_grupos"},
        1962: {"jogos": 3, "gols_pro": 3, "gols_contra": 4, "resultado": "fase_grupos"},
        1966: {"jogos": 3, "gols_pro": 1, "gols_contra": 3, "resultado": "fase_grupos"},
        1970: {"jogos": 4, "gols_pro": 6, "gols_contra": 4, "resultado": "quartas"},
        1978: {"jogos": 3, "gols_pro": 2, "gols_contra": 12, "resultado": "fase_grupos"},
        1986: {"jogos": 5, "gols_pro": 6, "gols_contra": 5, "resultado": "quartas"},
        1994: {"jogos": 4, "gols_pro": 3, "gols_contra": 4, "resultado": "oitavas"},
        1998: {"jogos": 4, "gols_pro": 8, "gols_contra": 6, "resultado": "oitavas"},
        2002: {"jogos": 4, "gols_pro": 4, "gols_contra": 4, "resultado": "oitavas"},
        2006: {"jogos": 4, "gols_pro": 5, "gols_contra": 5, "resultado": "oitavas"},
        2010: {"jogos": 4, "gols_pro": 4, "gols_contra": 5, "resultado": "oitavas"},
        2014: {"jogos": 4, "gols_pro": 5, "gols_contra": 3, "resultado": "oitavas"},
        2018: {"jogos": 4, "gols_pro": 3, "gols_contra": 6, "resultado": "oitavas"},
        2022: {"jogos": 3, "gols_pro": 2, "gols_contra": 3, "resultado": "fase_grupos"},
    },
}


def generate_supplement_from_historical() -> dict:
    """
    Gera dados suplementares a partir de dados historicos conhecidos.
    Nao requer API externa. Suporta multiplas selecoes.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "generated_at": datetime.now().isoformat(),
        "source": "historical_records",
        "teams": {},
    }

    print("Gerando dados suplementares a partir de registros historicos...")
    print("=" * 60)

    for team, team_data in HISTORICAL_DATA.items():
        print(f"\n{team}:")

        team_copas = []
        for year, data in sorted(team_data.items()):
            year_str = str(year)
            confidence = get_confidence_level(team, year_str)

            copa_data = {
                "ano": year,
                "season": year_str,
                "jogos": data["jogos"],
                "gols_marcados": data["gols_pro"],
                "gols_sofridos": data["gols_contra"],
                "saldo": data["gols_pro"] - data["gols_contra"],
                "resultado_final": data["resultado"],
                "nivel_confiabilidade": confidence,
                "fonte_tatica": "statsbomb" if confidence != "referencia" else None,
            }

            team_copas.append(copa_data)
            print(f"  {year}: {data['jogos']} jogos | {data['resultado']} | {confidence}")

        results["teams"][team] = {
            "copas": team_copas,
            "titulos": len([c for c in team_copas if c["resultado_final"] == "campeao"]),
            "total_jogos": sum(c["jogos"] for c in team_copas),
            "total_gols": sum(c["gols_marcados"] for c in team_copas),
        }

    # Salvar
    with open(SUPPLEMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"Dados salvos em {SUPPLEMENT_FILE}")
    print(f"Total: {len(results['teams'])} selecoes")

    return results


def load_supplement_data() -> dict | None:
    """Carrega dados suplementares do disco."""
    if SUPPLEMENT_FILE.exists():
        with open(SUPPLEMENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    print("=== INGESTAO DE DADOS SUPLEMENTARES ===")
    print()

    data = generate_supplement_from_historical()

    print()
    print("Resumo:")
    for team, team_data in data["teams"].items():
        titulos = team_data["titulos"]
        copas = len(team_data["copas"])
        print(f"  {team}: {copas} Copas, {titulos} titulo(s)")
