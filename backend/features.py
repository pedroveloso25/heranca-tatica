"""
Módulo de extração de features táticas.
Extrai métricas que capturam o estilo de jogo de cada time em cada partida.
"""

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).parent / "data"


def is_valid_location(loc) -> bool:
    """Verifica se uma localização é válida (list ou ndarray com 2+ elementos)."""
    if loc is None:
        return False
    if isinstance(loc, (list, np.ndarray)) and len(loc) >= 2:
        return True
    return False


def calculate_distance(loc1, loc2) -> float:
    """Calcula distância euclidiana entre duas coordenadas."""
    if not is_valid_location(loc1) or not is_valid_location(loc2):
        return 0.0
    return math.sqrt((loc2[0] - loc1[0])**2 + (loc2[1] - loc1[1])**2)


def extract_defensive_line_height(events: pd.DataFrame, team: str) -> float:
    """
    Calcula a altura média da linha defensiva.
    Usa a posição y média dos jogadores em ações defensivas.
    Campo StatsBomb: x vai de 0 (próprio gol) a 120 (gol adversário).
    """
    defensive_actions = events[
        (events["team"] == team) &
        (events["type"].isin(["Interception", "Block", "Clearance", "Tackle", "Duel"]))
    ]

    if defensive_actions.empty or "location" not in defensive_actions.columns:
        return 40.0  # valor padrão (meio campo)

    locations = defensive_actions["location"].dropna()
    if locations.empty:
        return 40.0

    # x representa a profundidade no campo (0 = próprio gol)
    x_positions = [loc[0] for loc in locations if is_valid_location(loc)]

    if not x_positions:
        return 40.0

    return float(np.mean(x_positions))


def extract_ppda(events: pd.DataFrame, team: str, opponent: str) -> float:
    """
    Calcula PPDA (Passes Permitidos por Ação Defensiva).
    Mede intensidade de pressão: quanto menor, mais intensa a marcação.
    Considera apenas ações no campo ofensivo (x > 60).
    """
    # Passes do adversário no campo defensivo deles (nosso campo ofensivo)
    opponent_passes = events[
        (events["team"] == opponent) &
        (events["type"] == "Pass")
    ]

    # Filtrar passes no terço defensivo do adversário (x < 60 para eles)
    opponent_passes_defensive = opponent_passes[
        opponent_passes["location"].apply(
            lambda loc: is_valid_location(loc) and loc[0] < 60
        )
    ]

    # Ações defensivas do time no campo ofensivo (x > 60)
    defensive_actions = events[
        (events["team"] == team) &
        (events["type"].isin(["Pressure", "Interception", "Tackle", "Foul Committed"]))
    ]

    defensive_high = defensive_actions[
        defensive_actions["location"].apply(
            lambda loc: is_valid_location(loc) and loc[0] > 60
        )
    ]

    n_passes = len(opponent_passes_defensive)
    n_actions = len(defensive_high)

    if n_actions == 0:
        return 20.0  # valor alto indica pouca pressão

    return float(n_passes / n_actions)


def extract_pass_length_profile(events: pd.DataFrame, team: str) -> tuple[float, float]:
    """
    Calcula perfil de comprimento de passes.
    Retorna (% passes curtos < 15m, % passes longos > 30m).
    """
    passes = events[
        (events["team"] == team) &
        (events["type"] == "Pass")
    ]

    if passes.empty:
        return 0.33, 0.33

    distances = []
    for _, p in passes.iterrows():
        loc = p.get("location")
        end_loc = p.get("pass_end_location")
        if is_valid_location(loc) and is_valid_location(end_loc):
            dist = calculate_distance(loc, end_loc)
            distances.append(dist)

    if not distances:
        return 0.33, 0.33

    total = len(distances)
    short = sum(1 for d in distances if d < 15) / total
    long = sum(1 for d in distances if d > 30) / total

    return float(short), float(long)


def extract_attack_width(events: pd.DataFrame, team: str) -> float:
    """
    Calcula largura de ataque.
    Mede a dispersão lateral (eixo y) em ações ofensivas no terço final.
    Campo StatsBomb: y vai de 0 a 80.
    """
    offensive_actions = events[
        (events["team"] == team) &
        (events["type"].isin(["Pass", "Carry", "Shot", "Dribble"]))
    ]

    # Filtrar ações no terço ofensivo (x > 80)
    final_third = offensive_actions[
        offensive_actions["location"].apply(
            lambda loc: is_valid_location(loc) and loc[0] > 80
        )
    ]

    if final_third.empty:
        return 40.0  # metade do campo

    y_positions = [
        loc[1] for loc in final_third["location"].dropna()
        if is_valid_location(loc)
    ]

    if len(y_positions) < 2:
        return 40.0

    # Largura = diferença entre posições mais extremas
    return float(max(y_positions) - min(y_positions))


def extract_transition_speed(events: pd.DataFrame, team: str) -> float:
    """
    Calcula velocidade de transição ofensiva.
    Mede a progressão média em x nos primeiros 10 segundos após recuperação.
    Valores altos indicam transições rápidas.
    """
    # Ordenar eventos por tempo
    events_sorted = events.sort_values(["minute", "second"]).reset_index(drop=True)

    # Encontrar recuperações de bola no campo defensivo
    recoveries = events_sorted[
        (events_sorted["team"] == team) &
        (events_sorted["type"].isin(["Ball Recovery", "Interception"]))
    ]

    if recoveries.empty:
        return 20.0  # valor padrão

    progressions = []

    for idx in recoveries.index:
        recovery = events_sorted.iloc[idx]
        rec_loc = recovery.get("location")

        if not is_valid_location(rec_loc):
            continue

        recovery_x = rec_loc[0]

        # Só considerar recuperações no campo defensivo
        if recovery_x > 60:
            continue

        recovery_time = recovery.get("minute", 0) * 60 + recovery.get("second", 0)

        # Procurar o avanço máximo nos próximos 10 segundos
        max_x = recovery_x
        for j in range(idx + 1, min(idx + 30, len(events_sorted))):
            evt = events_sorted.iloc[j]
            evt_time = evt.get("minute", 0) * 60 + evt.get("second", 0)

            if evt_time - recovery_time > 10:
                break

            if evt["team"] != team:
                break  # perdeu a posse

            loc = evt.get("location")
            if is_valid_location(loc):
                max_x = max(max_x, loc[0])

        progression = max_x - recovery_x
        if progression > 0:
            progressions.append(progression)

    if not progressions:
        return 20.0

    return float(np.mean(progressions))


def extract_cross_vs_central_ratio(events: pd.DataFrame, team: str) -> float:
    """
    Calcula razão entre cruzamentos e jogadas centrais.
    Valores altos indicam jogo mais pelas pontas.
    """
    passes = events[
        (events["team"] == team) &
        (events["type"] == "Pass")
    ]

    if passes.empty:
        return 0.5

    # Cruzamentos (coluna pass_cross existe)
    crosses = passes[passes.get("pass_cross", False) == True]
    n_crosses = len(crosses)

    # Passes centrais no terço final (y entre 25 e 55, x > 80)
    central_passes = passes[
        passes["location"].apply(
            lambda loc: (is_valid_location(loc) and loc[0] > 80 and 25 < loc[1] < 55)
        )
    ]
    n_central = len(central_passes)

    total = n_crosses + n_central
    if total == 0:
        return 0.5

    return float(n_crosses / total)


def extract_counterpressing_rate(events: pd.DataFrame, team: str) -> float:
    """
    Calcula taxa de pressão após perda (counterpressing).
    Proporção de perdas de bola seguidas de pressão em até 5 segundos.
    """
    # Eventos de perda de bola
    turnovers = events[
        (events["team"] == team) &
        (
            (events["type"] == "Dispossessed") |
            ((events["type"] == "Pass") & (events.get("pass_outcome", "") == "Incomplete")) |
            (events["type"] == "Miscontrol")
        )
    ].copy()

    if turnovers.empty:
        return 0.5

    counterpresses = 0

    for idx, turnover in turnovers.iterrows():
        turnover_time = turnover.get("minute", 0) * 60 + turnover.get("second", 0)

        # Procurar pressões nos próximos 5 segundos
        subsequent = events[
            (events.index > idx) &
            (events["team"] == team) &
            (events["type"] == "Pressure")
        ].head(5)

        for _, evt in subsequent.iterrows():
            evt_time = evt.get("minute", 0) * 60 + evt.get("second", 0)
            if evt_time - turnover_time <= 5:
                counterpresses += 1
                break
            if evt_time - turnover_time > 5:
                break

    return float(counterpresses / len(turnovers))


def extract_match_features(events: pd.DataFrame, team: str, opponent: str) -> dict[str, float]:
    """
    Extrai todas as features táticas de um jogo para um time.
    Retorna dicionário com as 7 features principais.
    """
    short_pass_pct, long_pass_pct = extract_pass_length_profile(events, team)

    return {
        "defensive_line_height": extract_defensive_line_height(events, team),
        "ppda": extract_ppda(events, team, opponent),
        "short_pass_pct": short_pass_pct,
        "long_pass_pct": long_pass_pct,
        "attack_width": extract_attack_width(events, team),
        "transition_speed": extract_transition_speed(events, team),
        "cross_vs_central": extract_cross_vs_central_ratio(events, team),
        "counterpress_rate": extract_counterpressing_rate(events, team),
    }


def extract_features_from_match_file(match_id: int, match_info: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extrai features de um arquivo de jogo salvo.
    Retorna lista com features para cada time.
    """
    events_path = DATA_DIR / "events" / f"match_{match_id}.parquet"

    if not events_path.exists():
        return []

    events = pd.read_parquet(events_path)

    home_team = match_info["home_team"]
    away_team = match_info["away_team"]

    home_features = extract_match_features(events, home_team, away_team)
    away_features = extract_match_features(events, away_team, home_team)

    return [
        {
            "match_id": match_id,
            "team": home_team,
            "season": match_info.get("season", ""),
            "opponent": away_team,
            "is_home": True,
            **home_features,
        },
        {
            "match_id": match_id,
            "team": away_team,
            "season": match_info.get("season", ""),
            "opponent": home_team,
            "is_home": False,
            **away_features,
        },
    ]


def extract_all_features() -> pd.DataFrame:
    """
    Extrai features de todos os jogos salvos.
    Retorna DataFrame com features por time por jogo.
    """
    metadata_path = DATA_DIR / "matches_metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError("Execute ingest.py primeiro para baixar os dados.")

    matches = pd.read_json(metadata_path)

    all_features = []

    for _, match in matches.iterrows():
        match_info = match.to_dict()
        features = extract_features_from_match_file(match["match_id"], match_info)
        all_features.extend(features)

    features_df = pd.DataFrame(all_features)

    # Salvar features extraídas
    features_df.to_json(DATA_DIR / "match_features.json", orient="records", indent=2)

    return features_df


def aggregate_team_features_by_tournament(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega features por time por Copa do Mundo.
    Calcula média das features de todos os jogos de uma seleção em uma edição.
    """
    feature_cols = [
        "defensive_line_height", "ppda", "short_pass_pct", "long_pass_pct",
        "attack_width", "transition_speed", "cross_vs_central", "counterpress_rate"
    ]

    aggregated = features_df.groupby(["team", "season"])[feature_cols].mean().reset_index()

    # Adicionar contagem de jogos
    match_counts = features_df.groupby(["team", "season"]).size().reset_index(name="n_matches")
    aggregated = aggregated.merge(match_counts, on=["team", "season"])

    # Salvar agregado
    aggregated.to_json(DATA_DIR / "team_tournament_features.json", orient="records", indent=2)

    return aggregated


if __name__ == "__main__":
    print("Extraindo features táticas...")
    print("=" * 60)

    try:
        features_df = extract_all_features()
        print(f"Features extraídas: {len(features_df)} registros")
        print(f"\nColunas: {list(features_df.columns)}")
        print(f"\nPrimeiras linhas:")
        print(features_df.head(10).to_string())

        print("\n" + "=" * 60)
        print("Agregando por time por Copa...")

        aggregated = aggregate_team_features_by_tournament(features_df)
        print(f"\nTimes por Copa: {len(aggregated)} registros")
        print(f"\nExemplo - Brasil:")
        brazil = aggregated[aggregated["team"] == "Brazil"]
        if not brazil.empty:
            print(brazil.to_string())
        else:
            print("Brasil não encontrado nos dados.")

    except FileNotFoundError as e:
        print(f"Erro: {e}")
