"""
Módulo de cálculo de similaridade vetorial.
Transforma features táticas em vetores e calcula similaridade entre edições.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).parent / "data"

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
