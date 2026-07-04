# Herança Tática ⚽

> *The statistical version of that argument that never ends between generations.*

I grew up as a sports fanatic, and the World Cup is the peak of it all for me. Taking advantage of the moment (and my hyperfocus that comes around every 4 years), I decided to mix the two things I love most: football and technology.

The result? **Herança Tática (Tactical Heritage)** — a web app that analyzes the tactical DNA of World Cup national teams from 1930 to 2022, displays each team's full historical record, and compares playing styles across different teams and eras.

*"Brazil today is way better than the 2006 squad."*
*"No way, you didn't see that team..."*

Now we have data.

🌐 **[copa-heranca-tatica.vercel.app](https://copa-heranca-tatica.vercel.app/)**

---

## What it does

- 📊 Compares tactical styles of the same national team across decades
- 🌍 Cross-compares any team vs any other team from any World Cup (1930–2022)
- 📈 Returns a similarity percentage with an explicit confidence level
- 🏆 Shows each team's full World Cup history: titles, games, goals, stages reached

---

## How it works

It wasn't all smooth — historical data is fragmented, and each era has a very different level of detail. But I found a way to mix them honestly: similarity is calculated using **only the features present in both sources**, and the confidence level tells you exactly how many metrics went into each comparison.

Up to 12 tactical metrics when the data allows:

| Metric | Description |
|---|---|
| Defensive line height | Average position of defenders (0–120) |
| PPDA | Passes allowed per defensive action — pressing intensity |
| Short passes % | Passes under 15m |
| Long passes % | Passes over 30m |
| Attack width | Average distance between widest attackers |
| Transition speed | Time from ball recovery to first forward pass |
| Cross vs central play | Crossing frequency vs central combinations |
| Counterpress rate | Pressure actions within 5s of losing the ball |
| Possession | Ball possession percentage |
| Shots on target | Shots on goal per game |
| Pass accuracy | Pass completion rate |
| xG | Expected goals |

**Confidence levels:**

🟢 **High** — 6+ features in common (both StatsBomb)
🟡 **Medium** — 3–5 features (mixed sources)
🔴 **Low** — 1–2 features (basic historical data only)

---

## Stack

- **Frontend:** React 18 + Vite + Tailwind CSS — deployed on Vercel
- **Backend:** Python 3.11 + FastAPI — deployed on Render
- **Tactical data:** [StatsBomb Open Data](https://github.com/statsbomb/open-data) (1970, 2018, 2022)
- **Historical data:** Compiled from public sources (1930–2014)

---

## Running locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open at `http://localhost:5173`

---

## Project structure

```
heranca-tatica/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── features.py          # Tactical feature extraction
│   ├── similarity.py        # Partial vector similarity engine
│   ├── ingest.py            # StatsBomb data pipeline
│   ├── ingest_supplement.py # Historical data supplement
│   └── data/                # Parquet files + historical JSON
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── TeamSelector.jsx
│           ├── SimilarityBar.jsx
│           ├── TacticCard.jsx
│           └── HistoryCard.jsx
└── README.md
```

---

Built it because I wanted to. Learned what I needed along the way. Had a lot of fun doing it.
