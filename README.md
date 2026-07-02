# Heranca Tatica

**O Brasil de 2022 joga mais parecido com o de 1970 ou com o de 2018?**

Este projeto responde essa pergunta transformando cada Copa do Mundo em um "DNA tatico" - um vetor numerico que captura *como* um time joga, nao *quanto* ele ganha.

## A Ideia

Resultados mentem. Um 1x0 sofrido pode esconder uma atuacao dominante. Um 4x0 pode vir de contra-ataques sem posse.

Heranca Tatica ignora placares e olha para o estilo: pressao alta ou bloco baixo? Passes curtos ou longos? Jogo pelas pontas ou pelo meio? Transicoes rapidas ou posse paciente?

Com isso, conseguimos comparar selecoes atraves das decadas e descobrir quais edicoes de um mesmo pais jogavam de forma similar - e quais eram completamente diferentes.

## O Que Voce Pode Fazer

**Comparar Edicoes de Uma Selecao**
- Selecione Brasil e veja como cada Copa (de 1958 a 2022) se compara com a mais recente
- Descubra que o Brasil de 1970 (86% similar) joga mais parecido com 2022 do que o Brasil de 2018 (82%)

**Comparar Duas Selecoes Quaisquer**
- Holanda 1974 vs Espanha 2010: 76% similar (tiki-taka antes do tiki-taka?)
- Argentina 1986 vs Argentina 2022: quao diferente era o time de Maradona?

**Ver Historico Completo**
- Todas as Copas de uma selecao com estatisticas, titulos e nivel de dados disponiveis

## Niveis de Confianca

Nem todos os dados sao iguais:

| Nivel | Features | Fonte | Copas |
|-------|----------|-------|-------|
| Alto | 12 features taticas | StatsBomb | 1958, 1962, 1970, 1974, 1986, 1990, 2018, 2022 |
| Medio | 4 features basicas | Dados historicos | 1966, 1978, 1982, 1994, 1998, 2002, 2006, 2010, 2014 |

Comparacoes entre Copas com dados diferentes usam apenas as features em comum. A interface mostra claramente o nivel de confianca de cada comparacao.

## Features Taticas

**Extraidas do StatsBomb (12 features):**
- Altura da Linha Defensiva
- PPDA (Pressao)
- % Passes Curtos / Longos
- Largura de Ataque
- Velocidade de Transicao
- Cruzamentos vs Central
- Taxa de Reacao a Perda (Counterpressing)
- Posse de Bola
- Chutes a Gol
- Precisao de Passes
- xG (Expected Goals)

## Stack Tecnica

```
Backend:  Python 3.11 + FastAPI
Frontend: React 18 + Vite + Tailwind CSS
Dados:    StatsBomb Open Data + Dados historicos compilados
Calculo:  Similaridade baseada em diferenca percentual normalizada
```

## Como Rodar

```bash
# Backend
cd backend
pip install -r requirements.txt
python ingest.py      # Baixa dados StatsBomb
python features.py    # Extrai features taticas
python main.py        # Roda API na porta 8080

# Frontend
cd frontend
npm install
npm run dev           # Roda em localhost:5173
```

## API

```
GET /api/teams              Lista selecoes disponiveis
GET /api/compare?team=X     Compara todas as edicoes de uma selecao
GET /api/compare-cross      Compara duas selecoes/anos quaisquer
GET /api/teams-years        Lista todos os times/anos disponiveis
GET /api/history?team=X     Historico completo de uma selecao
```

## Alguns Resultados Interessantes

**Brasil 2022 vs edicoes anteriores:**
| Copa | Similaridade | Confianca |
|------|--------------|-----------|
| 1970 | 86% | Alta |
| 1982 | 85% | Media |
| 2018 | 82% | Alta |
| 1962 | 75% | Alta |

**Times mais parecidos com Brasil 2022:**
1. Argentina 2022 (88%)
2. Franca 2022 (84%)
3. Brasil 1970 (86%)

---

*Dados taticos: StatsBomb Open Data. Dados historicos: FIFA/registros oficiais.*
