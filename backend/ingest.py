"""
Módulo de ingestão de dados da StatsBomb.
Baixa e processa todos os jogos de Copa do Mundo disponíveis.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from statsbombpy import sb


DATA_DIR = Path(__file__).parent / "data"


def get_world_cup_competitions() -> pd.DataFrame:
    """Retorna todas as edições de Copa do Mundo disponíveis na StatsBomb."""
    comps = sb.competitions()
    wc = comps[comps.competition_name == "FIFA World Cup"].copy()
    wc = wc.sort_values("season_id").reset_index(drop=True)
    return wc


def get_matches_for_competition(competition_id: int, season_id: int) -> pd.DataFrame:
    """Retorna todos os jogos de uma competição/temporada específica."""
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    return matches


def get_events_for_match(match_id: int) -> pd.DataFrame:
    """Retorna todos os eventos de um jogo específico."""
    events = sb.events(match_id=match_id)
    return events


def process_match_events(events: pd.DataFrame, match_info: dict[str, Any]) -> dict[str, Any]:
    """
    Processa os eventos de um jogo e retorna um dicionário com metadados e eventos.
    Separa eventos por time para facilitar a extração de features.
    """
    home_team = match_info["home_team"]
    away_team = match_info["away_team"]

    # Separar eventos por time
    home_events = events[events["team"] == home_team].copy()
    away_events = events[events["team"] == away_team].copy()

    return {
        "match_id": match_info["match_id"],
        "competition": match_info.get("competition", "FIFA World Cup"),
        "season": match_info.get("season", ""),
        "home_team": home_team,
        "away_team": away_team,
        "home_score": match_info.get("home_score", 0),
        "away_score": match_info.get("away_score", 0),
        "match_date": str(match_info.get("match_date", "")),
        "home_events_count": len(home_events),
        "away_events_count": len(away_events),
    }


def ingest_all_world_cups(save_raw: bool = True) -> pd.DataFrame:
    """
    Baixa todos os jogos de todas as Copas do Mundo disponíveis.
    Retorna um DataFrame com metadados de todos os jogos processados.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    wc_comps = get_world_cup_competitions()
    print(f"Encontradas {len(wc_comps)} edições de Copa do Mundo:")
    print(wc_comps[["competition_id", "season_name", "season_id"]].to_string())
    print()

    all_matches_meta = []
    all_events = {}

    for _, comp in wc_comps.iterrows():
        comp_id = comp["competition_id"]
        season_id = comp["season_id"]
        season_name = comp["season_name"]

        print(f"Processando Copa do Mundo {season_name}...")

        matches = get_matches_for_competition(comp_id, season_id)
        print(f"  {len(matches)} jogos encontrados")

        for _, match in matches.iterrows():
            match_id = match["match_id"]
            match_info = {
                "match_id": match_id,
                "competition": "FIFA World Cup",
                "season": season_name,
                "home_team": match["home_team"],
                "away_team": match["away_team"],
                "home_score": match.get("home_score", 0),
                "away_score": match.get("away_score", 0),
                "match_date": str(match.get("match_date", "")),
            }

            try:
                events = get_events_for_match(match_id)
                match_meta = process_match_events(events, match_info)
                all_matches_meta.append(match_meta)

                # Armazena eventos para extração de features
                all_events[match_id] = {
                    "info": match_info,
                    "events": events,
                }

            except Exception as e:
                print(f"    Erro ao processar jogo {match_id}: {e}")
                continue

    # Criar DataFrame com metadados
    matches_df = pd.DataFrame(all_matches_meta)

    if save_raw:
        # Salvar metadados em JSON
        matches_df.to_json(DATA_DIR / "matches_metadata.json", orient="records", indent=2)

        # Salvar eventos em arquivos separados por jogo (evita arquivos gigantes)
        events_dir = DATA_DIR / "events"
        events_dir.mkdir(exist_ok=True)

        for match_id, data in all_events.items():
            events_df = data["events"]
            # Salvar como parquet para eficiência
            events_df.to_parquet(events_dir / f"match_{match_id}.parquet")

        print(f"\nDados salvos em {DATA_DIR}")
        print(f"  - {len(matches_df)} jogos processados")
        print(f"  - Eventos salvos em {events_dir}")

    return matches_df, all_events


def load_match_events(match_id: int) -> pd.DataFrame | None:
    """Carrega eventos de um jogo já processado do disco."""
    events_path = DATA_DIR / "events" / f"match_{match_id}.parquet"
    if events_path.exists():
        return pd.read_parquet(events_path)
    return None


def load_matches_metadata() -> pd.DataFrame | None:
    """Carrega metadados de jogos já processados."""
    meta_path = DATA_DIR / "matches_metadata.json"
    if meta_path.exists():
        return pd.read_json(meta_path)
    return None


if __name__ == "__main__":
    # Executa ingestão completa
    print("Iniciando ingestão de dados da Copa do Mundo...")
    print("=" * 60)

    matches_df, events = ingest_all_world_cups(save_raw=True)

    print("\n" + "=" * 60)
    print("Resumo da ingestão:")
    print(f"Total de jogos: {len(matches_df)}")
    print("\nJogos por edição:")
    print(matches_df.groupby("season").size().to_string())

    print("\nSeleções únicas:")
    all_teams = set(matches_df["home_team"].unique()) | set(matches_df["away_team"].unique())
    print(f"Total: {len(all_teams)} seleções")
