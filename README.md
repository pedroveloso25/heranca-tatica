# Herança Tática

**O Brasil de 2022 joga mais parecido com o de 1970 ou com o de 2018?**

Este projeto responde a essa pergunta transformando cada Copa do Mundo em um "DNA tático" — um vetor numérico que captura *como* um time joga, não *quanto* ele ganha.

## A Ideia

Resultados mentem. Um 1x0 sofrido pode esconder uma atuação dominante. Um 4x0 pode vir de contra-ataques sem posse.

Herança Tática ignora placares e olha para o estilo: pressão alta ou bloco baixo? Passes curtos ou longos? Jogo pelas pontas ou pelo meio? Transições rápidas ou posse paciente?

Com isso, conseguimos comparar seleções através das décadas e descobrir quais edições de um mesmo país jogavam de forma similar — e quais eram completamente diferentes.

## O Que Você Pode Fazer

**Comparar Edições de Uma Seleção**
- Selecione Brasil e veja como cada Copa (de 1958 a 2022) se compara com a mais recente.
- Descubra que o Brasil de 1970 (86% similar) joga mais parecido com 2022 do que o Brasil de 2018 (82%).

**Comparar Duas Seleções Quaisquer**
- Holanda 1974 vs Espanha 2010: 76% similar (tiki-taka antes do tiki-taka?)
- Argentina 1986 vs Argentina 2022: quão diferente era o time de Maradona?

**Ver Histórico Completo**
- Todas as Copas de uma seleção com estatísticas, títulos e nível de dados disponíveis.

## Níveis de Confiança

Nem todos os dados são iguais:

| Nível | Features | Fonte | Copas |
|-------|----------|-------|-------|
| Alto | 12 features táticas | StatsBomb | 1958, 1962, 1970, 1974, 1986, 1990, 2018, 2022 |
| Médio | 4 features básicas | Dados históricos | 1966, 1978, 1982, 1994, 1998, 2002, 2006, 2010, 2014 |

Comparações entre Copas com dados diferentes usam apenas as features em comum. A interface mostra claramente o nível de confiança de cada comparação.

## Features Táticas

**Extraídas do StatsBomb (12 features):**
- Altura da Linha Defensiva
- PPDA (Pressão)
- % Passes Curtos / Longos
- Largura de Ataque
- Velocidade de Transição
- Cruzamentos vs Central
- Taxa de Reação à Perda (Counterpressing)
- Posse de Bola
- Chutes a Gol
- Precisão de Passes
- xG (Expected Goals)

## Stack Técnica

```text
Backend:  Python 3.11 + FastAPI
Frontend: React 18 + Vite + Tailwind CSS
Dados:    StatsBomb Open Data + Dados históricos compilados
Cálculo:  Similaridade baseada em diferença percentual normalizada
```

## Como Rodar

```bash
# Backend
cd backend
pip install -r requirements.txt
python ingest.py      # Baixa dados StatsBomb
python features.py    # Extrai features táticas
python main.py        # Roda API na porta 8080

# Frontend
cd frontend
npm install
npm run dev           # Roda em localhost:5173
```

## API

```text
GET /api/teams              Lista seleções disponíveis
GET /api/compare?team=X     Compara todas as edições de uma seleção
GET /api/compare-cross      Compara duas seleções/anos quaisquer
GET /api/teams-years        Lista todos os times/anos disponíveis
GET /api/history?team=X     Histórico completo de uma seleção
```

## Alguns Resultados Interessantes

**Brasil 2022 vs edições anteriores:**

| Copa | Similaridade | Confiança |
|------|--------------|-----------|
| 1970 | 86% | Alta |
| 1982 | 85% | Média |
| 2018 | 82% | Alta |
| 1962 | 75% | Alta |

**Times mais parecidos com Brasil 2022:**
1. Argentina 2022 (88%)
2. França 2022 (84%)
3. Brasil 1970 (86%)

---

*Dados táticos: StatsBomb Open Data. Dados históricos: FIFA/registros oficiais.*
