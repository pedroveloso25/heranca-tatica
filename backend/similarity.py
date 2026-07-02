"""
Módulo de cálculo de similaridade vetorial.
Transforma features táticas em vetores e calcula similaridade entre edições.

REGRA CRÍTICA: Ao comparar vetores de fontes diferentes, usar APENAS
features presentes em ambas as fontes.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).parent / "data"

# Features do StatsBomb (dados completos)
FEATURE_COLS = [
    "defensive_line_height",
    "ppda",
    "short_pass_pct",
    "long_pass_pct",
    "attack_width",
    "transition_speed",
    "cross_vs_central",
    "counterpress_rate",
]

# Features disponíveis por fonte
# NOTA: StatsBomb atualmente só exporta features táticas avançadas
# As features básicas (posse, chutes, etc.) precisariam ser extraídas separadamente
FEATURES_BY_SOURCE = {
    "statsbomb": [
        "defensive_line_height", "ppda", "short_pass_pct", "long_pass_pct",
        "attack_width", "transition_speed", "cross_vs_central", "counterpress_rate"
    ],
    "static_historical": [
        "posse", "chutes_gol", "precisao_passes", "xg"
    ]
}

# Features que podem ser comparadas entre quaisquer fontes
# (quando ambas têm os dados básicos)
UNIVERSAL_FEATURES = ["posse", "chutes_gol", "precisao_passes", "xg"]

# TODAS as features possíveis (para calcular features_missing)
ALL_FEATURES = [
    "defensive_line_height", "ppda", "short_pass_pct", "long_pass_pct",
    "attack_width", "transition_speed", "cross_vs_central", "counterpress_rate",
    "posse", "chutes_gol", "precisao_passes", "xg"
]

# Mapeamento de nomes de features para exibição
FEATURE_DISPLAY_NAMES = {
    "defensive_line_height": "Altura da Linha",
    "ppda": "PPDA",
    "short_pass_pct": "Passes Curtos",
    "long_pass_pct": "Passes Longos",
    "attack_width": "Largura Ataque",
    "transition_speed": "Vel. Transição",
    "cross_vs_central": "Cruzamentos",
    "counterpress_rate": "Reação à Perda",
    "posse": "Posse de Bola",
    "chutes_gol": "Chutes a Gol",
    "precisao_passes": "Precisão Passes",
    "xg": "xG"
}

FEATURE_UNITS = {
    "defensive_line_height": "m",
    "ppda": "",
    "short_pass_pct": "%",
    "long_pass_pct": "%",
    "attack_width": "m",
    "transition_speed": "m",
    "cross_vs_central": "%",
    "counterpress_rate": "%",
    "posse": "%",
    "chutes_gol": "",
    "precisao_passes": "%",
    "xg": ""
}


def load_team_tournament_features() -> pd.DataFrame:
    """Carrega features agregadas por time por Copa."""
    path = DATA_DIR / "team_tournament_features.json"
    if not path.exists():
        raise FileNotFoundError("Execute features.py primeiro para extrair features.")
    return pd.read_json(path)


def create_tactical_vectors(df: pd.DataFrame) -> tuple[np.ndarray, StandardScaler]:
    """
    Normaliza features e cria vetores táticos.
    Retorna matriz de vetores e o scaler usado.
    """
    features = df[FEATURE_COLS].values

    scaler = StandardScaler()
    vectors = scaler.fit_transform(features)

    return vectors, scaler


def apply_pca(vectors: np.ndarray, n_components: int = 5) -> tuple[np.ndarray, PCA]:
    """
    Aplica PCA para reduzir dimensionalidade (opcional).
    Retorna vetores reduzidos e o modelo PCA.
    """
    n_components = min(n_components, vectors.shape[1], vectors.shape[0])
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(vectors)
    return reduced, pca


def calculate_similarity_matrix(vectors: np.ndarray) -> np.ndarray:
    """Calcula matriz de similaridade de cosseno entre todos os vetores."""
    return cosine_similarity(vectors)


def get_team_editions(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Retorna todas as edições de Copa de uma seleção."""
    return df[df["team"] == team].sort_values("season").reset_index(drop=True)


def compare_team_editions(
    df: pd.DataFrame,
    team: str,
    reference_season: str | None = None
) -> list[dict[str, Any]]:
    """
    Compara edições de uma seleção com a mais recente (ou referência especificada).
    Retorna lista ordenada por similaridade.
    """
    team_df = get_team_editions(df, team)

    if team_df.empty:
        return []

    if reference_season is None:
        # Pegar a edição mais recente
        reference_season = team_df["season"].iloc[-1]

    # Converter para comparação consistente
    reference_idx = team_df[team_df["season"].astype(str) == str(reference_season)].index
    if reference_idx.empty:
        return []

    reference_idx = reference_idx[0]

    # Criar vetores apenas para este time
    vectors, _ = create_tactical_vectors(team_df)

    # Calcular similaridade
    sim_matrix = calculate_similarity_matrix(vectors)

    # Pegar similaridades da edição de referência
    ref_row_idx = team_df.index.get_loc(reference_idx)
    similarities = sim_matrix[ref_row_idx]

    results = []
    for i, (_, row) in enumerate(team_df.iterrows()):
        if str(row["season"]) == str(reference_season):
            continue

        results.append({
            "team": str(team),
            "season": str(row["season"]),
            "similarity": float(similarities[i]),
            "n_matches": int(row["n_matches"]),
            "features": {col: float(row[col]) for col in FEATURE_COLS},
        })

    # Ordenar por similaridade (maior primeiro)
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results


def get_all_teams() -> list[str]:
    """Retorna lista de todas as seleções disponíveis."""
    df = load_team_tournament_features()
    teams = sorted(df["team"].unique().tolist())
    return teams


def get_team_history(team: str) -> dict[str, Any]:
    """
    Retorna histórico completo de uma seleção.
    Inclui features de cada edição e comparações.
    """
    df = load_team_tournament_features()
    team_df = get_team_editions(df, team)

    if team_df.empty:
        return {"team": team, "editions": [], "comparisons": []}

    # Pegar a edição mais recente como referência
    latest_season = str(team_df["season"].iloc[-1])

    editions = []
    for _, row in team_df.iterrows():
        editions.append({
            "season": str(row["season"]),
            "n_matches": int(row["n_matches"]),
            "features": {col: float(row[col]) for col in FEATURE_COLS},
        })

    comparisons = compare_team_editions(df, team, latest_season)

    return {
        "team": team,
        "reference_season": latest_season,
        "editions": editions,
        "comparisons": comparisons,
    }


def compare_all_team_editions(team: str, reference_year: int | None = None) -> dict[str, Any]:
    """
    Compara TODAS as edições de um time usando compare_partial.
    Inclui tanto edições StatsBomb quanto históricas.

    Args:
        team: Nome do time
        reference_year: Ano de referência (default: mais recente)

    Returns:
        {
            "team": str,
            "reference": {year, source, n_matches, features...},
            "comparisons": [
                {
                    "year": 2002,
                    "similarity": 0.71,
                    "confidence": "medium",
                    "features_used": [...],
                    "features_missing": [...],
                    "total_features_used": 4,
                    "source": "static_historical",
                    "n_matches": 7
                },
                ...
            ]
        }
    """
    # Obter todos os anos disponíveis para este time
    all_years = get_available_teams_years()
    team_years = [ty for ty in all_years if ty["team"] == team]

    if not team_years:
        return {"team": team, "reference": None, "comparisons": []}

    # Ordenar por ano (mais recente primeiro)
    team_years.sort(key=lambda x: x["year"], reverse=True)

    # Determinar ano de referência
    if reference_year is None:
        reference_year = team_years[0]["year"]

    # Carregar dados da referência
    ref_data = get_team_data(team, reference_year)
    if not ref_data:
        return {"team": team, "reference": None, "comparisons": []}

    comparisons = []

    for ty in team_years:
        year = ty["year"]
        if year == reference_year:
            continue  # Pular a própria referência

        # Carregar dados desta edição
        edition_data = get_team_data(team, year, prefer_source=ty["source"])
        if not edition_data:
            continue

        # Comparar usando compare_partial
        result = compare_partial(ref_data, edition_data)

        if result is None:  # "insufficient" confidence
            continue

        comparisons.append({
            "year": year,
            "similarity": result["similarity"],
            "confidence": result["confidence"],
            "features_used": result["features_used"],
            "features_missing": result["features_missing"],
            "total_features_used": result["total_features_used"],
            "source": edition_data.get("source", "unknown"),
            "n_matches": edition_data.get("n_matches", 0),
        })

    # Ordenar por similaridade (maior primeiro)
    comparisons.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "team": team,
        "reference": {
            "year": reference_year,
            "source": ref_data.get("source", "unknown"),
            "n_matches": ref_data.get("n_matches", 0),
            # Incluir todas as features disponíveis
            "features": {f: ref_data.get(f) for f in ALL_FEATURES if ref_data.get(f) is not None}
        },
        "comparisons": comparisons,
    }


def find_similar_teams(
    df: pd.DataFrame,
    team: str,
    season: str,
    top_n: int = 10
) -> list[dict[str, Any]]:
    """
    Encontra times/edições mais similares a uma seleção específica em uma Copa.
    """
    target = df[(df["team"] == team) & (df["season"].astype(str) == str(season))]

    if target.empty:
        return []

    target_idx = target.index[0]

    # Criar vetores para todos os times
    vectors, _ = create_tactical_vectors(df)
    sim_matrix = calculate_similarity_matrix(vectors)

    # Pegar similaridades do time alvo
    row_idx = df.index.get_loc(target_idx)
    similarities = sim_matrix[row_idx]

    results = []
    for i, (_, row) in enumerate(df.iterrows()):
        if str(row["team"]) == str(team) and str(row["season"]) == str(season):
            continue

        results.append({
            "team": str(row["team"]),
            "season": str(row["season"]),
            "similarity": float(similarities[i]),
            "n_matches": int(row["n_matches"]),
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_n]


def save_vectors() -> None:
    """Salva vetores táticos normalizados em arquivo .npy."""
    df = load_team_tournament_features()
    vectors, scaler = create_tactical_vectors(df)

    # Salvar vetores
    np.save(DATA_DIR / "tactical_vectors.npy", vectors)

    # Salvar metadados dos vetores (time, edição)
    metadata = df[["team", "season", "n_matches"]].to_dict(orient="records")
    import json
    with open(DATA_DIR / "vectors_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Vetores salvos: {vectors.shape}")


# =============================================================================
# COMPARAÇÃO CROSS-SELEÇÃO (Etapa 2)
# =============================================================================

def get_common_features(source1: str, source2: str) -> list[str]:
    """
    Retorna features em comum entre duas fontes.
    REGRA CRÍTICA: Use apenas estas features ao comparar vetores.
    """
    # Se as fontes são iguais, retornar todas as features da fonte
    if source1 == source2:
        return FEATURES_BY_SOURCE.get(source1, [])

    # Se fontes diferentes, verificar interseção
    features1 = set(FEATURES_BY_SOURCE.get(source1, []))
    features2 = set(FEATURES_BY_SOURCE.get(source2, []))
    return sorted(list(features1 & features2))


def get_confidence_level(n_features: int) -> str:
    """
    Determina nível de confiança baseado na quantidade de features em comum.
    - high: >= 6 features (ambos StatsBomb)
    - medium: 3-5 features (StatsBomb + histórico)
    - low: 1-2 features (só posse + chutes)
    - insufficient: 0 features
    """
    if n_features >= 6:
        return "high"
    elif n_features >= 3:
        return "medium"
    elif n_features >= 1:
        return "low"
    else:
        return "insufficient"


def compare_partial(
    data1: dict,
    data2: dict,
    candidate_features: list[str] | None = None
) -> dict[str, Any] | None:
    """
    Compara dois vetores de features usando APENAS as features presentes em ambos.

    Args:
        data1: Dict com features do time 1 (valores podem ser None/NaN)
        data2: Dict com features do time 2 (valores podem ser None/NaN)
        candidate_features: Lista de features a considerar (default: ALL_FEATURES)

    Returns:
        Dict com:
        - similarity: float (0-1)
        - confidence: "high" | "medium" | "low" | "insufficient"
        - features_used: lista de features usadas no cálculo
        - features_missing: lista de features que faltaram
        - feature_comparison: detalhes de cada feature comparada

        Retorna None se confidence == "insufficient"
    """
    if candidate_features is None:
        candidate_features = ALL_FEATURES

    features_used = []
    features_missing = []
    values1 = []
    values2 = []
    feature_comparison = []

    for feature in candidate_features:
        v1 = data1.get(feature)
        v2 = data2.get(feature)

        # Verificar se ambos têm valor válido (não None, não NaN)
        v1_valid = v1 is not None and not (isinstance(v1, float) and np.isnan(v1))
        v2_valid = v2 is not None and not (isinstance(v2, float) and np.isnan(v2))

        if v1_valid and v2_valid:
            features_used.append(feature)
            values1.append(float(v1))
            values2.append(float(v2))
            feature_comparison.append({
                "name": feature,
                "display_name": FEATURE_DISPLAY_NAMES.get(feature, feature),
                "team1_value": float(v1),
                "team2_value": float(v2),
                "unit": FEATURE_UNITS.get(feature, "")
            })
        else:
            features_missing.append(feature)

    # Determinar confiança
    n_features = len(features_used)
    confidence = get_confidence_level(n_features)

    # Se insufficient, retornar None
    if confidence == "insufficient":
        return None

    # Calcular similaridade baseada em diferença percentual média
    vec1 = np.array(values1)
    vec2 = np.array(values2)

    differences = []
    for v1, v2 in zip(vec1, vec2):
        max_val = max(abs(v1), abs(v2), 0.001)  # evitar div/0
        diff_pct = abs(v1 - v2) / max_val
        differences.append(diff_pct)

    avg_diff = np.mean(differences)
    similarity = float(np.exp(-avg_diff * 2))  # fator 2 para sensibilidade

    return {
        "similarity": round(similarity, 4),
        "confidence": confidence,
        "features_used": features_used,
        "features_missing": features_missing,
        "total_features_used": n_features,
        "feature_comparison": feature_comparison
    }


def load_historical_team_data(team: str, year: int) -> dict | None:
    """Carrega dados de um time de historical_cups.json."""
    from ingest_fbref import load_historical_cups, get_team_features_historical
    return get_team_features_historical(team, year)


def load_statsbomb_team_data(team: str, year: int) -> dict | None:
    """Carrega dados de um time do StatsBomb (inclui features táticas + básicas)."""
    try:
        df = load_team_tournament_features()
        # Converter season para string para comparação
        team_data = df[(df["team"] == team) & (df["season"].astype(str) == str(year))]

        if team_data.empty:
            return None

        row = team_data.iloc[0]

        # Extrair TODAS as features disponíveis (táticas + básicas)
        features = {}
        for col in ALL_FEATURES:
            if col in row.index:
                val = row[col]
                # Converter para float se não for None/NaN
                if val is not None and not (isinstance(val, float) and np.isnan(val)):
                    features[col] = float(val)
                else:
                    features[col] = None

        return {
            "team": team,
            "year": year,
            "source": "statsbomb",
            "n_matches": int(row.get("n_matches", 0)),
            "confidence": "high",
            **features
        }
    except FileNotFoundError:
        return None


def get_team_data(team: str, year: int, prefer_source: str | None = None) -> dict | None:
    """
    Obtém dados de um time, tentando primeiro StatsBomb, depois histórico.
    Retorna dict com source indicando a origem dos dados.

    Args:
        prefer_source: Se especificado, tenta essa fonte primeiro
    """
    if prefer_source == "static_historical":
        # Tentar histórico primeiro
        data = load_historical_team_data(team, year)
        if data:
            return data
        # Fallback para StatsBomb
        return load_statsbomb_team_data(team, year)

    # Padrão: StatsBomb primeiro
    data = load_statsbomb_team_data(team, year)
    if data:
        return data

    # Fallback para histórico
    return load_historical_team_data(team, year)


def get_team_data_best_match(team1: str, year1: int, team2: str, year2: int) -> tuple[dict, dict]:
    """
    Obtém dados de dois times priorizando fontes compatíveis.
    Tenta encontrar a melhor combinação de fontes que permite comparação.
    """
    # Primeiro, tentar obter com preferências padrão
    data1_sb = load_statsbomb_team_data(team1, year1)
    data1_hist = load_historical_team_data(team1, year1)
    data2_sb = load_statsbomb_team_data(team2, year2)
    data2_hist = load_historical_team_data(team2, year2)

    # Opções de combinação (em ordem de preferência)
    options = []

    # 1. Ambos StatsBomb (melhor qualidade)
    if data1_sb and data2_sb:
        common = get_common_features("statsbomb", "statsbomb")
        options.append((data1_sb, data2_sb, len(common), "statsbomb-statsbomb"))

    # 2. Ambos históricos
    if data1_hist and data2_hist:
        common = get_common_features("static_historical", "static_historical")
        options.append((data1_hist, data2_hist, len(common), "historical-historical"))

    # 3. Mix (geralmente sem features em comum, mas tentar)
    if data1_sb and data2_hist:
        common = get_common_features("statsbomb", "static_historical")
        if common:
            options.append((data1_sb, data2_hist, len(common), "mix"))

    if data1_hist and data2_sb:
        common = get_common_features("static_historical", "statsbomb")
        if common:
            options.append((data1_hist, data2_sb, len(common), "mix"))

    # Escolher a opção com mais features em comum
    if not options:
        # Usar o que tiver disponível
        data1 = data1_sb or data1_hist
        data2 = data2_sb or data2_hist
        if not data1 or not data2:
            raise ValueError(f"Dados não encontrados para um ou ambos os times")
        return data1, data2

    # Ordenar por número de features em comum (maior primeiro)
    options.sort(key=lambda x: x[2], reverse=True)
    return options[0][0], options[0][1]


def compare_cross_teams(
    team1: str, year1: int,
    team2: str, year2: int
) -> dict[str, Any]:
    """
    Compara dois times de quaisquer Copas, usando apenas features em comum.

    Usa compare_partial() para calcular similaridade com base nas features
    disponíveis em ambos os vetores.

    Retorna:
    {
        "team1": {...},
        "team2": {...},
        "similarity": 0.87,
        "confidence": "medium",
        "features_used": [...],
        "features_missing": [...],
        "feature_comparison": [...]
    }
    """
    # Carregar dados dos dois times priorizando fontes compatíveis
    data1, data2 = get_team_data_best_match(team1, year1, team2, year2)

    source1 = data1.get("source", "unknown")
    source2 = data2.get("source", "unknown")

    # Usar compare_partial para cálculo
    result = compare_partial(data1, data2)

    if result is None:
        raise ValueError(f"Nenhuma feature em comum entre {team1} {year1} e {team2} {year2}")

    return {
        "team1": {
            "name": team1,
            "year": year1,
            "source": source1,
            "n_matches": data1.get("n_matches", 0)
        },
        "team2": {
            "name": team2,
            "year": year2,
            "source": source2,
            "n_matches": data2.get("n_matches", 0)
        },
        "similarity": result["similarity"],
        "confidence": result["confidence"],
        "features_used": result["features_used"],
        "features_missing": result["features_missing"],
        "n_features": result["total_features_used"],
        "feature_comparison": result["feature_comparison"]
    }


def get_available_teams_years() -> list[dict]:
    """
    Retorna lista de todos os times/anos disponíveis de todas as fontes.
    """
    teams_years = []

    # StatsBomb
    try:
        df = load_team_tournament_features()
        for _, row in df.iterrows():
            teams_years.append({
                "team": row["team"],
                "year": int(str(row["season"])[:4]),
                "source": "statsbomb"
            })
    except FileNotFoundError:
        pass

    # Histórico
    try:
        from ingest_fbref import load_historical_cups
        hist_df = load_historical_cups()
        if not hist_df.empty:
            for (team, year), _ in hist_df.groupby(["team", "year"]):
                # Evitar duplicatas
                if not any(t["team"] == team and t["year"] == int(year) for t in teams_years):
                    teams_years.append({
                        "team": team,
                        "year": int(year),  # Converter para int nativo
                        "source": "static_historical"
                    })
    except Exception:
        pass

    return sorted(teams_years, key=lambda x: (x["team"], x["year"]))


if __name__ == "__main__":
    print("Calculando similaridades...")
    print("=" * 60)

    try:
        df = load_team_tournament_features()
        print(f"Dados carregados: {len(df)} registros")

        # Listar times
        teams = get_all_teams()
        print(f"\nSeleções disponíveis: {len(teams)}")
        print(teams[:20], "..." if len(teams) > 20 else "")

        # Exemplo: Brasil
        print("\n" + "=" * 60)
        print("Exemplo: Comparação das edições do Brasil")

        brazil_history = get_team_history("Brazil")
        if brazil_history["editions"]:
            print(f"\nEdições do Brasil: {len(brazil_history['editions'])}")
            for ed in brazil_history["editions"]:
                print(f"  - {ed['season']}: {ed['n_matches']} jogos")

            print(f"\nComparação com {brazil_history['reference_season']}:")
            for comp in brazil_history["comparisons"]:
                print(f"  {comp['season']}: {comp['similarity']:.3f}")

        # Salvar vetores
        print("\n" + "=" * 60)
        save_vectors()

    except FileNotFoundError as e:
        print(f"Erro: {e}")
