"""
Ingestão de dados do FBref para Copas do Mundo históricas.
Extrai estatísticas agregadas por time por Copa (1966-2014).
"""

import logging
import time
from pathlib import Path
from io import StringIO

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Headers para simular navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

DATA_DIR = Path(__file__).parent / "data"

# Anos das Copas disponíveis no FBref
COPA_YEARS = [1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014]

# Anos com xG disponível
XG_AVAILABLE_FROM = 2006

# Features disponíveis por fonte (tabela de referência)
FEATURES_BY_SOURCE = {
    "statsbomb": [
        "altura_linha", "ppda", "passes_curtos", "passes_longos",
        "largura_ataque", "vel_transicao", "cruzamentos", "counterpress",
        "posse", "chutes_gol", "precisao_passes", "pressoes", "xg"
    ],
    "fbref": [
        "posse", "chutes_gol", "precisao_passes", "pressoes", "xg"  # xg só a partir de 2006
    ],
    "copa2026": [
        "posse", "chutes_gol", "precisao_passes"
    ]
}

# Features comuns entre fontes
COMMON_FEATURES_STATSBOMB_FBREF = ["posse", "chutes_gol", "precisao_passes", "pressoes", "xg"]
COMMON_FEATURES_ALL = ["posse", "chutes_gol", "precisao_passes"]


def get_fbref_url(year: int) -> str:
    """Gera URL do FBref para uma Copa específica."""
    return f"https://fbref.com/en/comps/1/{year}/stats/{year}-World-Cup-Stats"


def parse_possession(val) -> float | None:
    """Converte valor de posse para float."""
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.replace('%', '').strip()
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_numeric(val) -> float | None:
    """Converte valor numérico genérico."""
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def get_fbref_matches(year: int) -> pd.DataFrame | None:
    """
    Extrai estatísticas de uma Copa do Mundo do FBref.

    Retorna DataFrame com colunas:
    - team, year, possession, shots, shots_on_target, xg,
      passes_attempted, pass_pct, pressures, tackles, fouls, source
    """
    url = get_fbref_url(year)
    logger.info(f"Buscando dados da Copa {year}: {url}")

    try:
        # Fazer requisição com headers para evitar bloqueio
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        # FBref tem várias tabelas, precisamos encontrar a de estatísticas de time
        tables = pd.read_html(StringIO(response.text), header=0)

        if not tables:
            logger.warning(f"Nenhuma tabela encontrada para {year}")
            return None

        # A tabela principal geralmente é a maior ou tem "Squad" como coluna
        main_table = None
        for i, table in enumerate(tables):
            cols = [str(c).lower() for c in table.columns.tolist()]
            # Procurar tabela com Squad/Team
            if any('squad' in c or 'team' in c for c in cols):
                # Preferir tabela maior
                if main_table is None or len(table) > len(main_table):
                    main_table = table
                    logger.debug(f"Tabela {i} selecionada como principal ({len(table)} linhas)")

        if main_table is None:
            # Tentar usar a primeira tabela grande
            main_table = max(tables, key=len)
            logger.warning(f"Usando maior tabela como fallback ({len(main_table)} linhas)")

        # Normalizar nomes de colunas
        main_table.columns = [str(c).strip() for c in main_table.columns]

        # Mapeamento de colunas do FBref para nosso schema
        # FBref usa nomes variados, então precisamos ser flexíveis
        col_mapping = {
            'team': ['Squad', 'squad', 'Team', 'team'],
            'possession': ['Poss', 'poss', 'Possession', 'possession'],
            'shots': ['Sh', 'sh', 'Shots', 'shots'],
            'shots_on_target': ['SoT', 'sot', 'Shots on Target', 'SoT%'],
            'xg': ['xG', 'xg', 'Expected Goals'],
            'passes_attempted': ['Att', 'att', 'Passes Attempted', 'Total'],
            'pass_pct': ['Cmp%', 'cmp%', 'Pass%', 'pass%', 'Completion %'],
            'pressures': ['Press', 'press', 'Pressures'],
            'tackles': ['Tkl', 'tkl', 'Tackles'],
            'fouls': ['Fls', 'fls', 'Fouls']
        }

        def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
            """Encontra coluna correspondente no DataFrame."""
            for col in df.columns:
                col_lower = str(col).lower().strip()
                for candidate in candidates:
                    if candidate.lower() in col_lower or col_lower in candidate.lower():
                        return col
            return None

        # Construir DataFrame normalizado
        records = []

        team_col = find_column(main_table, col_mapping['team'])
        if not team_col:
            logger.error(f"Coluna de time não encontrada para {year}")
            logger.debug(f"Colunas disponíveis: {main_table.columns.tolist()}")
            return None

        for _, row in main_table.iterrows():
            team = row.get(team_col)
            if pd.isna(team) or not isinstance(team, str) or len(team) < 2:
                continue

            # Limpar nome do time (remover códigos de país, etc)
            team = team.strip()

            record = {
                'team': team,
                'year': year,
                'source': 'fbref'
            }

            # Extrair cada feature
            for feature, candidates in col_mapping.items():
                if feature == 'team':
                    continue

                col = find_column(main_table, candidates)
                if col:
                    if feature == 'possession':
                        record[feature] = parse_possession(row.get(col))
                    else:
                        record[feature] = parse_numeric(row.get(col))
                else:
                    record[feature] = None

            # xG só disponível a partir de 2006
            if year < XG_AVAILABLE_FROM:
                record['xg'] = None

            records.append(record)

        if not records:
            logger.warning(f"Nenhum registro extraído para {year}")
            return None

        df = pd.DataFrame(records)
        logger.info(f"Copa {year}: {len(df)} times extraídos")

        return df

    except Exception as e:
        logger.error(f"Erro ao processar Copa {year}: {e}")
        return None


def ingest_all_fbref(years: list[int] | None = None, delay: float = 2.0) -> dict[int, pd.DataFrame]:
    """
    Baixa dados de todas as Copas especificadas.

    Args:
        years: Lista de anos para processar (default: COPA_YEARS)
        delay: Delay entre requisições em segundos (respeitar rate limit)

    Returns:
        Dicionário {ano: DataFrame}
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if years is None:
        years = COPA_YEARS

    results = {}

    for i, year in enumerate(years):
        df = get_fbref_matches(year)

        if df is not None and not df.empty:
            # Salvar parquet
            output_path = DATA_DIR / f"fbref_{year}.parquet"
            df.to_parquet(output_path)
            logger.info(f"Salvo: {output_path}")
            results[year] = df

        # Delay entre requisições (exceto última)
        if i < len(years) - 1:
            logger.debug(f"Aguardando {delay}s antes da próxima requisição...")
            time.sleep(delay)

    return results


def load_fbref_data(year: int) -> pd.DataFrame | None:
    """Carrega dados do FBref já salvos."""
    path = DATA_DIR / f"fbref_{year}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


def load_all_fbref_data() -> pd.DataFrame:
    """Carrega todos os dados FBref salvos em um único DataFrame."""
    all_dfs = []

    for year in COPA_YEARS:
        df = load_fbref_data(year)
        if df is not None:
            all_dfs.append(df)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()


def load_historical_cups() -> pd.DataFrame:
    """
    Carrega dados históricos estáticos de historical_cups.json.
    Retorna DataFrame com source='static_historical'.
    """
    path = DATA_DIR / "historical_cups.json"
    if not path.exists():
        logger.warning(f"Arquivo não encontrado: {path}")
        return pd.DataFrame()

    import json
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data['matches'])
    df['source'] = 'static_historical'

    # Renomear colunas para padrão interno
    df = df.rename(columns={
        'shots_on_target': 'chutes_gol',
        'possession': 'posse',
        'pass_accuracy': 'precisao_passes',
        'shots': 'chutes'
    })

    logger.info(f"Carregados {len(df)} jogos históricos de {path}")
    return df


def aggregate_historical_by_team_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega dados históricos por time/ano.
    Retorna médias das features por seleção por Copa.
    """
    if df.empty:
        return pd.DataFrame()

    # Features numéricas para agregar
    numeric_cols = ['posse', 'chutes', 'chutes_gol', 'xg', 'precisao_passes',
                    'goals_for', 'goals_against']
    available_cols = [c for c in numeric_cols if c in df.columns]

    # Agrupar por time e ano
    agg_dict = {col: 'mean' for col in available_cols}
    agg_dict['confidence'] = 'first'  # manter confiança
    agg_dict['source'] = 'first'

    aggregated = df.groupby(['team', 'year']).agg(agg_dict).reset_index()

    # Adicionar contagem de jogos
    match_counts = df.groupby(['team', 'year']).size().reset_index(name='n_matches')
    aggregated = aggregated.merge(match_counts, on=['team', 'year'])

    return aggregated


def get_team_features_historical(team: str, year: int) -> dict | None:
    """
    Obtém features de uma seleção em uma Copa específica dos dados históricos.
    Retorna None se não encontrado.
    """
    df = load_historical_cups()
    if df.empty:
        return None

    team_data = df[(df['team'] == team) & (df['year'] == year)]
    if team_data.empty:
        return None

    # Agregar jogos do time naquela Copa
    features = {
        'team': team,
        'year': year,
        'source': 'static_historical',
        'n_matches': len(team_data),
        'posse': team_data['posse'].mean() if 'posse' in team_data else None,
        'chutes_gol': team_data['chutes_gol'].mean() if 'chutes_gol' in team_data else None,
        'precisao_passes': team_data['precisao_passes'].mean() if 'precisao_passes' in team_data else None,
        'xg': team_data['xg'].mean() if 'xg' in team_data and team_data['xg'].notna().any() else None,
        'confidence': team_data['confidence'].iloc[0] if 'confidence' in team_data else 'medium'
    }

    return features


def get_available_features(source: str, year: int | None = None) -> list[str]:
    """
    Retorna features disponíveis para uma fonte/ano.

    IMPORTANTE: Use esta função para saber quais features comparar.
    """
    features = FEATURES_BY_SOURCE.get(source, []).copy()

    # xG só disponível no FBref a partir de 2006
    if source == 'fbref' and year is not None and year < XG_AVAILABLE_FROM:
        if 'xg' in features:
            features.remove('xg')

    return features


def get_common_features(source1: str, source2: str, year1: int | None = None, year2: int | None = None) -> list[str]:
    """
    Retorna features em comum entre duas fontes.

    REGRA CRÍTICA: Ao comparar vetores, use APENAS estas features.
    """
    features1 = set(get_available_features(source1, year1))
    features2 = set(get_available_features(source2, year2))
    return list(features1 & features2)


if __name__ == "__main__":
    print("=" * 60)
    print("Ingestão de dados FBref - Copas do Mundo 1966-2014")
    print("=" * 60)

    # Testar com uma Copa primeiro
    print("\nTestando com Copa de 2010...")
    df_2010 = get_fbref_matches(2010)

    if df_2010 is not None:
        print(f"\nSample da Copa 2010:")
        print(df_2010.head(10).to_string())
        print(f"\nColunas: {df_2010.columns.tolist()}")
        print(f"\nTipos: {df_2010.dtypes.to_string()}")
    else:
        print("Falha ao extrair dados de 2010")

    # Descomentar para ingestão completa:
    # print("\n" + "=" * 60)
    # print("Iniciando ingestão completa...")
    # results = ingest_all_fbref()
    # print(f"\nTotal: {len(results)} Copas processadas")
