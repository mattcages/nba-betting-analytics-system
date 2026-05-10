# NBA Betting Analytics System

Advanced Python-based analytics system that evaluates NBA player performance, defensive matchups, and betting value using real data from the NBA API.

This project was built for sports data analysis, predictive insights, and betting evaluation using statistical performance trends.

---

## Features

### Player Analysis
- Evaluates individual player performance
- Detects “hot streaks” (recent form vs season average)
- Home vs away performance comparison
- 3-point shooting trends (FG3M / FG3A)

### Team Defense Analysis
- League-wide defensive ranking system
- Opponent defensive strength evaluation
- Defensive adjustment applied to projections

### Matchup Analysis
- Offensive vs defensive matchup simulation
- Player-by-player projection for specific games
- Betting “value score” system

### Data Collection System
- Automatically scans NBA playoff teams
- Collects roster + player stats
- Saves structured datasets locally
- Builds historical performance logs

---

## How It Works

The system combines:

- Recent player performance (last 3–5 games)
- Season averages
- Playoff vs regular season differences
- Opponent defensive ranking
- Game context (home/away, volume trends)

Then it generates:

- Projection values
- Betting signals (Over / Risk / Value)
- Confidence score based on multiple factors

---

## Project Structure

```bash
NBA_PROJECT/
│
├── analyzers/
│   ├── analise_individual.py      # Player performance analyzer
│   ├── analise_confronto.py      # Matchup evaluator
│
├── data_collector/
│   ├── playoff_scanner.py        # NBA data scraper
│
├── outputs/                      # Generated reports (auto)
├── requirements.txt
├── .gitignore
└── README.md
