"""
API FastAPI para Herança Tática.
Endpoints para comparação de seleções e visualização de dados táticos.
"""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from similarity import (
    load_team_tournament_features,
    get_all_teams,
    get_team_history,
    compare_team_editions,
    compare_all_team_editions,
    find_similar_teams,
    compare_cross_teams,
    get_available_teams_years,
    FEATURE_COLS,
    ALL_FEATURES,
    FEATURE_DISPLAY_NAMES,
)
from ingest_supplement import load_supplement_data, STATSBOMB_COVERAGE


app = FastAPI(
    title="Herança Tática API",
    description="Análise do DNA tático histórico das seleções da Copa do Mundo",
    version="1.0.0",
)

# Configurar CORS para o frontend (local e producao)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://copa-heranca-tatica.vercel.app",
        "https://*.vercel.app",
        "https://copa-heranca-tatica-git-main-pedroveloso25s-projects.vercel.app/",
        "https://copa-heranca-tatica.vercel.app/",
        "https://copa-heranca-tatica-5r5emq98r-pedroveloso25s-projects.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mapeamento de seleções para códigos ISO de bandeiras
TEAM_FLAGS = {
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Brazil": "br",
    "Bulgaria": "bg",
    "Cameroon": "cm",
    "Canada": "ca",
    "Chile": "cl",
    "Colombia": "co",
    "Costa Rica": "cr",
    "Croatia": "hr",
    "Czech Republic": "cz",
    "Czechoslovakia": "cz",
    "Denmark": "dk",
    "Ecuador": "ec",
    "Egypt": "eg",
    "England": "gb-eng",
    "France": "fr",
    "Germany": "de",
    "Germany DR": "de",
    "West Germany": "de",
    "Ghana": "gh",
    "Greece": "gr",
    "Haiti": "ht",
    "Hungary": "hu",
    "Iran": "ir",
    "Iraq": "iq",
    "Ireland": "ie",
    "Italy": "it",
    "Japan": "jp",
    "Korea Republic": "kr",
    "South Korea": "kr",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "Nigeria": "ng",
    "Northern Ireland": "gb-nir",
    "Norway": "no",
    "Panama": "pa",
    "Paraguay": "py",
    "Peru": "pe",
    "Poland": "pl",
    "Portugal": "pt",
    "Qatar": "qa",
    "Romania": "ro",
    "Russia": "ru",
    "Saudi Arabia": "sa",
    "Scotland": "gb-sct",
    "Senegal": "sn",
    "Serbia": "rs",
    "Slovenia": "si",
    "South Africa": "za",
    "Soviet Union": "ru",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Tunisia": "tn",
    "Turkey": "tr",
    "Ukraine": "ua",
    "United Arab Emirates": "ae",
    "United States": "us",
    "Uruguay": "uy",
    "Wales": "gb-wls",
    "Yugoslavia": "rs",
    "Zaire": "cd",
}


def get_flag_url(team: str) -> str:
    """Retorna URL da bandeira de uma seleção."""
    code = TEAM_FLAGS.get(team, "un")  # UN flag como fallback
    return f"https://flagcdn.com/{code}.svg"


@app.get("/")
def root() -> dict[str, str]:
    """Endpoint raiz com informações da API."""
    return {
        "name": "Herança Tática API",
        "version": "1.0.0",
        "description": "Análise do DNA tático histórico das seleções da Copa do Mundo",
    }


@app.get("/api/teams")
def list_teams() -> dict[str, Any]:
    """Lista todas as seleções disponíveis."""
    try:
        teams = get_all_teams()
        return {
            "teams": [
                {"name": team, "flag_url": get_flag_url(team)}
                for team in teams
            ],
            "total": len(teams),
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Dados ainda não processados. Execute ingest.py e features.py primeiro.")


@app.get("/api/team/{team}")
def get_team(team: str) -> dict[str, Any]:
    """Retorna histórico completo de uma seleção."""
    try:
        history = get_team_history(team)

        if not history["editions"]:
            raise HTTPException(status_code=404, detail=f"Seleção '{team}' não encontrada.")

        # Adicionar URL da bandeira
        history["flag_url"] = get_flag_url(team)

        return history
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Dados ainda não processados.")


@app.get("/api/compare")
def compare(
    team: str = Query(..., description="Nome da seleção"),
    reference: int | None = Query(None, description="Ano de referência (ex: 2022)")
) -> dict[str, Any]:
    """
    Compara TODAS as edições de uma seleção usando compare_partial.
    Inclui edições StatsBomb e históricas, com nível de confiança.

    Cada comparação retorna:
    - year, similarity, confidence, features_used, features_missing, source

    Copas com confidence "insufficient" (0 features) são excluídas.
    """
    try:
        result = compare_all_team_editions(team, reference)

        if result["reference"] is None:
            raise HTTPException(status_code=404, detail=f"Seleção '{team}' não encontrada.")

        return {
            "team": team,
            "flag_url": get_flag_url(team),
            "reference": {
                "year": result["reference"]["year"],
                "season": str(result["reference"]["year"]),  # compatibilidade
                "source": result["reference"]["source"],
                "features": result["reference"]["features"],
                "n_matches": result["reference"]["n_matches"],
            },
            "comparisons": result["comparisons"],
            "feature_names": ALL_FEATURES,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Dados ainda não processados.")


@app.get("/api/similar")
def similar_teams(
    team: str = Query(..., description="Nome da seleção"),
    season: str = Query(..., description="Edição da Copa (ex: 2022)"),
    top_n: int = Query(10, description="Número de resultados", ge=1, le=50)
) -> dict[str, Any]:
    """
    Encontra times/edições mais similares a uma seleção em uma Copa específica.
    """
    try:
        df = load_team_tournament_features()
        results = find_similar_teams(df, team, season, top_n)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Seleção '{team}' na edição '{season}' não encontrada."
            )

        # Adicionar flags
        for r in results:
            r["flag_url"] = get_flag_url(r["team"])

        return {
            "team": team,
            "season": season,
            "flag_url": get_flag_url(team),
            "similar": results,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Dados ainda não processados.")


@app.get("/api/features")
def get_features() -> dict[str, Any]:
    """Retorna descrição das features táticas utilizadas."""
    return {
        "features": [
            {
                "name": "defensive_line_height",
                "display_name": "Altura da Linha Defensiva",
                "description": "Posição média dos zagueiros no eixo vertical (0-120). Valores altos indicam linha alta.",
                "unit": "metros",
            },
            {
                "name": "ppda",
                "display_name": "PPDA",
                "description": "Passes Permitidos por Ação Defensiva. Quanto menor, mais intensa a pressão.",
                "unit": "passes/ação",
            },
            {
                "name": "short_pass_pct",
                "display_name": "% Passes Curtos",
                "description": "Proporção de passes com menos de 15 metros.",
                "unit": "%",
            },
            {
                "name": "long_pass_pct",
                "display_name": "% Passes Longos",
                "description": "Proporção de passes com mais de 30 metros.",
                "unit": "%",
            },
            {
                "name": "attack_width",
                "display_name": "Largura de Ataque",
                "description": "Dispersão lateral em ações ofensivas no terço final.",
                "unit": "metros",
            },
            {
                "name": "transition_speed",
                "display_name": "Velocidade de Transição",
                "description": "Tempo médio entre recuperação e chegada ao campo ofensivo.",
                "unit": "segundos",
            },
            {
                "name": "cross_vs_central",
                "display_name": "Cruzamentos vs Central",
                "description": "Razão entre cruzamentos e jogadas pelo meio. Valores altos = jogo mais aberto.",
                "unit": "razão",
            },
            {
                "name": "counterpress_rate",
                "display_name": "Taxa de Reação à Perda",
                "description": "Proporção de perdas seguidas de pressão imediata (5s).",
                "unit": "%",
            },
        ]
    }


@app.get("/api/compare-cross")
def compare_cross(
    team1: str = Query(..., description="Nome da primeira seleção"),
    year1: int = Query(..., description="Ano da Copa da primeira seleção"),
    team2: str = Query(..., description="Nome da segunda seleção"),
    year2: int = Query(..., description="Ano da Copa da segunda seleção")
) -> dict[str, Any]:
    """
    Compara duas seleções de quaisquer Copas.

    Usa apenas features disponíveis em ambas as fontes de dados.
    Retorna similaridade, confiança e comparação feature a feature.

    Níveis de confiança:
    - high: >= 6 features em comum (ambos StatsBomb)
    - medium: 3-5 features em comum
    - low: < 3 features em comum
    """
    try:
        result = compare_cross_teams(team1, year1, team2, year2)

        # Adicionar flags
        result["team1"]["flag_url"] = get_flag_url(team1)
        result["team2"]["flag_url"] = get_flag_url(team2)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comparar: {str(e)}")


@app.get("/api/teams-years")
def list_teams_years() -> dict[str, Any]:
    """
    Lista todos os times/anos disponíveis de todas as fontes.
    Útil para popular dropdowns de comparação.
    """
    try:
        teams_years = get_available_teams_years()

        # Agrupar por time
        by_team = {}
        for item in teams_years:
            team = item["team"]
            if team not in by_team:
                by_team[team] = {
                    "name": team,
                    "flag_url": get_flag_url(team),
                    "years": []
                }
            by_team[team]["years"].append({
                "year": item["year"],
                "source": item["source"]
            })

        # Ordenar anos de cada time (mais recente primeiro)
        for team in by_team:
            by_team[team]["years"].sort(key=lambda x: x["year"], reverse=True)

        return {
            "teams": list(by_team.values()),
            "total_teams": len(by_team),
            "total_entries": len(teams_years)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@app.get("/api/history")
def get_history(
    team: str = Query("Brazil", description="Nome da selecao")
) -> dict[str, Any]:
    """
    Retorna historico completo de uma selecao em todas as Copas do Mundo.
    Inclui nivel de confiabilidade dos dados para cada edicao.

    Niveis:
    - completo: Dados taticos completos do StatsBomb (>=3 jogos)
    - parcial: Dados taticos limitados do StatsBomb (<3 jogos)
    - referencia: Apenas dados historicos basicos (sem features taticas)
    """
    supplement = load_supplement_data()

    if not supplement:
        raise HTTPException(
            status_code=503,
            detail="Dados suplementares nao encontrados. Execute ingest_supplement.py primeiro."
        )

    # Nova estrutura: supplement["teams"][team]
    teams_data = supplement.get("teams", {})

    if team not in teams_data:
        available = list(teams_data.keys())[:5]
        raise HTTPException(
            status_code=404,
            detail=f"Dados historicos para '{team}' nao disponiveis. Disponiveis: {available}..."
        )

    team_supplement = teams_data[team]

    # Carregar dados taticos do StatsBomb onde disponiveis
    try:
        df = load_team_tournament_features()
        team_history = get_team_history(team)
        statsbomb_editions = {e["season"]: e for e in team_history.get("editions", [])}
    except FileNotFoundError:
        statsbomb_editions = {}

    copas = []
    for copa in team_supplement["copas"]:
        season = copa["season"]
        nivel = copa["nivel_confiabilidade"]

        entry = {
            "ano": copa["ano"],
            "season": season,
            "jogos": copa["jogos"],
            "gols_marcados": copa["gols_marcados"],
            "gols_sofridos": copa["gols_sofridos"],
            "saldo": copa["saldo"],
            "resultado_final": copa["resultado_final"],
            "nivel_confiabilidade": nivel,
            "tem_dados_taticos": nivel != "referencia",
            "confiavel_para_comparacao": nivel == "completo",
        }

        # Adicionar dados taticos se disponiveis
        if season in statsbomb_editions:
            sb_data = statsbomb_editions[season]
            entry["n_matches_statsbomb"] = sb_data.get("n_matches", 0)
            entry["features"] = sb_data.get("features", {})

            # Aviso para dados parciais
            if nivel == "parcial":
                entry["aviso"] = f"Baseado em {sb_data.get('n_matches', 0)} jogo(s). Baixa confiabilidade estatistica."
        else:
            entry["n_matches_statsbomb"] = 0
            entry["features"] = None

        copas.append(entry)

    # Estatisticas gerais
    titulos = [c for c in copas if c["resultado_final"] == "campeao"]
    vices = [c for c in copas if c["resultado_final"] == "vice"]
    total_jogos = sum(c["jogos"] for c in copas)
    total_gols = sum(c["gols_marcados"] for c in copas)

    return {
        "team": team,
        "flag_url": get_flag_url(team),
        "generated_at": supplement["generated_at"],
        "estatisticas": {
            "copas_disputadas": len(copas),
            "titulos": len(titulos),
            "anos_titulos": [c["ano"] for c in titulos],
            "vices": len(vices),
            "total_jogos": total_jogos,
            "total_gols": total_gols,
            "media_gols_por_copa": round(total_gols / len(copas), 1) if copas else 0,
        },
        "cobertura": {
            "completo": [c["ano"] for c in copas if c["nivel_confiabilidade"] == "completo"],
            "parcial": [c["ano"] for c in copas if c["nivel_confiabilidade"] == "parcial"],
            "referencia": [c["ano"] for c in copas if c["nivel_confiabilidade"] == "referencia"],
        },
        "copas": copas,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
