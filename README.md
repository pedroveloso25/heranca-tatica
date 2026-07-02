# Herança Tática

Análise do DNA tático histórico das seleções da Copa do Mundo.

## O que faz

Transforma cada jogo de Copa em um vetor numérico que captura o estilo de jogo (não o resultado), e usa esses vetores para comparar edições históricas de uma seleção.

Exemplo: "O Brasil de 2022 joga mais parecido com o de 1974 ou com o de 2018?"

## Stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Dados**: StatsBomb Open Data (via statsbombpy)
- **Similaridade**: scikit-learn (cosine similarity)

## Features Táticas Extraídas

1. **Altura da Linha Defensiva** - Posição média dos zagueiros
2. **PPDA** - Passes permitidos por ação defensiva (pressão)
3. **% Passes Curtos** - Passes com menos de 15m
4. **% Passes Longos** - Passes com mais de 30m
5. **Largura de Ataque** - Dispersão lateral no terço final
6. **Velocidade de Transição** - Progressão em 10s após recuperação
7. **Cruzamentos vs Central** - Proporção de jogo pelas pontas
8. **Taxa de Reação à Perda** - Counterpressing em 5 segundos

## Copas Disponíveis

1958, 1962, 1970, 1974, 1986, 1990, 2018, 2022

## Como Rodar

### Backend

```bash
cd backend
pip install -r requirements.txt

# Primeira vez: baixar e processar dados
python ingest.py
python features.py

# Rodar API
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173

## API Endpoints

- `GET /api/teams` - Lista todas as seleções
- `GET /api/compare?team=Brazil` - Compara edições de uma seleção
- `GET /api/similar?team=Brazil&season=2022` - Encontra times similares
- `GET /api/features` - Descrição das features táticas

## Exemplos de Resultados

### Brasil 2022 vs edições anteriores:
- 1974: 46% similar (maior)
- 1970: 34% similar
- 2018: 7% similar
- 1990: -30% (diferente)
- 1962: -58% (muito diferente)

### Times mais similares ao Brasil 2022:
1. Argentina 2022 (90%)
2. Brasil 1974 (82%)
3. Portugal 2022 (73%)
