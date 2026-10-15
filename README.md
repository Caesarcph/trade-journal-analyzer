# 📔 TradeJournal Analyzer

> Trading journal analyzer that computes statistics from your trade history, highlights time-based patterns, and suggests improvements.

[![CI](https://github.com/Caesarcph/trade-journal-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/Caesarcph/trade-journal-analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📌 Status

**Early-stage Python library. There is no CLI and no dashboard yet; you use it from Python.**

What works today:
- `Trade` data model and SQLite storage (`TradeDatabase`: save / load all trades)
- CSV / Excel (`.xlsx`) import with automatic column-name matching (e.g. `Side`, `Lots`, `PnL`, `Open Time`)
- Analyzers: basic statistics, drawdown analysis, time-based patterns (hour, weekday, month, session, session overlap,
  seasonality) and a rule-based performance scorer / trade grader
- 18 pytest tests, run in CI

Planned (not implemented yet): MT4/MT5 import, broker statement import (Interactive Brokers, TD Ameritrade),
MT5 auto-sync, pattern recognition, LLM insights, Streamlit dashboard, export, YAML configuration.
See [ROADMAP.md](ROADMAP.md).

## 🎯 Why This Tool?

Most traders keep journals but never analyze them properly. This tool:

- 📊 **Imports** trades from CSV/Excel (MT4/MT5 and broker imports planned)
- 🔍 **Finds time-based patterns** in your winning and losing trades
- 🏅 **Scores and grades** your performance with simple, transparent rules
- 🧠 **AI-powered insights** using LLM analysis (planned)
- 📈 **Visualizes** your trading performance over time (planned dashboard)

## ✨ Features

### Import & Sync
- ✅ CSV/Excel import with automatic column mapping (header aliases) or an explicit `column_mapping`
- ✅ Order-type normalization (`BUY`/`SELL`, `LONG`/`SHORT`, `0`/`1`, `OP_BUY`/`OP_SELL`)
- 🗓️ Import from MT4/MT5 history (planned)
- 🗓️ Import from broker statements (Interactive Brokers, TD Ameritrade) (planned)
- 🗓️ Auto-sync with MT5 (live updates) (planned)

### Analytics
- ✅ Win rate, profit factor, expectancy, average win/loss, largest win/loss, consecutive wins/losses
- ✅ Net profit by symbol, profit per trading day
- ✅ Win rate / PnL by hour, day of week, month, trading session, session overlap and time period
- ✅ Drawdown analysis: max / current / average drawdown, drawdown periods, recovery time
- ✅ Holding time analysis (average duration of all, winning and losing trades)
- ✅ Average win / average loss ratio (used in the performance score)
- 🗓️ Win rate by timeframe (planned; the `Trade` model has no timeframe field yet)
- 🗓️ Entry accuracy (how close to optimal entry?) (planned)

### Performance Scoring
- ✅ Overall score and letter grade (A–F) from win rate, risk management and profit factor
- ✅ Per-trade grades with feedback, grade distribution, text report
- ✅ Rule-based strengths / weaknesses / recommendations

### Pattern Recognition
- ✅ Time-based performance patterns and text recommendations (`TimeAnalysis.recommendations()`)
- 🗓️ What conditions lead to your best trades? (planned)
- 🗓️ What patterns precede losing streaks? (planned)
- 🗓️ Emotional pattern detection (revenge trades, FOMO) (planned)

### AI Insights (planned)
- 🤖 LLM-powered trade review
- 💡 Personalized improvement suggestions
- 📝 Automated trade journaling prompts

## 🏗️ Project Structure

```
trade-journal-analyzer/
├── src/
│   ├── importers/
│   │   └── csv_importer.py       # CSV / Excel import with column auto-mapping
│   ├── analyzers/
│   │   ├── basic_stats.py        # Win rate, PnL, expectancy, etc.
│   │   ├── time_analysis.py      # Time-based patterns, sessions, overlaps, seasonality
│   │   ├── drawdown.py           # Drawdown analysis
│   │   └── performance_scorer.py # Overall score, trade grades, report
│   ├── models/
│   │   └── trade.py              # Trade data model
│   ├── storage/
│   │   └── database.py           # SQLite storage
│   ├── config/                   # Empty placeholder package
│   └── dashboard/                # Empty placeholder package (dashboard planned)
├── tests/                        # pytest suite
├── .github/workflows/ci.yml      # CI: pytest on Python 3.11
├── pytest.ini
├── requirements.txt
├── TIME_ANALYSIS_ENHANCEMENTS.md # Notes on the time-analysis features
├── ROADMAP.md
├── CONTRIBUTING.md
└── LICENSE
```

Planned modules (not created yet): `importers/mt5_importer.py`, `mt4_importer.py`, `ib_importer.py`,
`analyzers/pattern_finder.py`, `llm_analyzer.py`, `dashboard/app.py` and pages, `models/journal_entry.py`,
`storage/export.py`, `config/settings.yaml`.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Caesarcph/trade-journal-analyzer.git
cd trade-journal-analyzer
pip install -r requirements.txt

# Run the tests
pytest
```

### Import Your Trades

There is no command-line interface yet. Run Python from the repository root:

```python
from src.importers import CSVImporter
from src.storage.database import TradeDatabase

# Column names are matched automatically (e.g. "Ticket", "Symbol", "Side", "Lots",
# "Open Time", "Open Price", "Close Time", "Close Price", "PnL").
trades = CSVImporter("trades.csv").import_trades()      # .xlsx works too

# Or map columns explicitly: {Trade field: column name in your file}.
# An explicit mapping turns auto-detection off; unmapped fields must be named exactly
# like the Trade fields (ticket, symbol, open_time, open_price, ...).
trades = CSVImporter("trades.csv", column_mapping={"order_type": "Side", "profit": "PnL"}).import_trades()

# Optional: persist to SQLite
db = TradeDatabase("trades.db")
for t in trades:
    db.save_trade(t)
trades = db.get_trades()
```

Rows without `symbol` or `open_time` are skipped. MT4/MT5 and Interactive Brokers importers are planned.

### Launch Dashboard (planned)

A Streamlit dashboard is planned but not implemented yet (`src/dashboard/` is an empty package).

## 📈 Analytics Deep Dive

All examples assume `trades` is a list of `Trade` objects (see above).

### Basic Statistics

```python
from src.analyzers import BasicStats

analyzer = BasicStats(trades)
stats = analyzer.get_stats()

print(f"Total Trades: {stats.total_trades}")
print(f"Win Rate: {stats.win_rate:.1%}")
print(f"Profit Factor: {stats.profit_factor:.2f}")
print(f"Average Win: ${stats.avg_win:.2f}")
print(f"Average Loss: ${stats.avg_loss:.2f}")
print(f"Expectancy: ${stats.expectancy:.2f}/trade")
print(f"Max Drawdown: {stats.max_drawdown:.1f}% (${stats.max_drawdown_amount:.2f})")
print(f"Profit by symbol: {stats.profit_per_trade}")
print(f"Avg holding time: {stats.avg_trade_duration / 3600:.1f} h")

print(analyzer.summary())    # formatted text summary
analyzer.to_dict()           # dict version
```

### Drawdown Analysis

```python
from decimal import Decimal
from src.analyzers import DrawdownAnalyzer

dd_analyzer = DrawdownAnalyzer(trades, initial_balance=Decimal("10000"))
res = dd_analyzer.get_analysis()

print(f"Max Drawdown: ${res.max_drawdown:,.2f} ({res.max_drawdown_pct:.2f}%)")
print(f"Current Drawdown: ${res.current_drawdown:,.2f}")
print(f"Average Recovery Time: {res.average_recovery_time}")

# List all significant drawdowns
for dd in res.drawdown_periods:
    if dd.max_depth_pct > 5.0:  # Only show > 5% drawdowns
        print(f"Drawdown: -{dd.max_depth_pct:.1f}% | Duration: {dd.duration}")
```

### Time-Based Analysis

Trades are bucketed by **close time**. Sessions are defined in UTC: Asian 00–08, London 08–16, New_York 13–21,
London_NY_Overlap 13–16 (a trade can count in more than one session).

```python
from src.analyzers import TimeAnalysis

time_analyzer = TimeAnalysis(trades)

# Performance by day of week (keys 0=Monday ... 6=Sunday)
day_perf = time_analyzer.by_day_of_week()
# {0: {'name': 'Monday', 'total_trades': 1, 'wins': 1, 'losses': 0, 'win_rate': 1.0,
#      'loss_rate': 0.0, 'total_pnl': 50.0, 'avg_pnl': 50.0}, ...}

# Performance by hour (0-23), month (1-12), session and time period
hour_perf = time_analyzer.by_hour()
month_perf = time_analyzer.by_month()
session_perf = time_analyzer.by_session()
# {'London': {'total_trades': 3, 'win_rate': 0.67, 'avg_pnl': 33.33, ...},
#  'New_York': {...}, 'London_NY_Overlap': {...}}
period_perf = time_analyzer.by_period()
# {'market_open': {...}, 'midday': {...}, 'afternoon': {...}, ...}

# Best / worst hours (need >= 3 trades per hour) and weekdays (>= 5 trades per weekday);
# empty when no bucket has enough trades
peak_hours = time_analyzer.get_peak_hours(limit=5)
worst_hours = time_analyzer.get_worst_hours(limit=3)
best_weekday = time_analyzer.get_best_weekday()
worst_weekday = time_analyzer.get_worst_weekday()

# Session overlaps
overlaps = time_analyzer.get_session_overlaps()
# [{'session_pair': 'London-New_York', 'overlap_name': 'London/New_York Overlap',
#   'overlap_window_utc': ('13:00', '16:00'), 'total_trades': 2, 'win_rate': 0.5, 'avg_pnl': 10.0, ...}]
best_overlap = time_analyzer.get_best_session_overlap()

# Profit dispersion and streaks per session
volatility = time_analyzer.get_session_volatility_analysis()
# {'London': {'total_trades': 3, 'profit_range': (-30.0, 80.0), 'profit_std': 56.86,
#             'max_winning_streak': 1, 'max_losing_streak': 1, ...}, ...}

# Time-based risk metrics
risk_metrics = time_analyzer.get_time_based_risk_metrics()
# keys: 'overall', 'by_hour', 'by_session', 'by_weekday'
# risk_metrics['overall'] -> {'total_trades', 'max_drawdown', 'sharpe_ratio', 'profit_factor', ...}

# Seasonality
seasonal = time_analyzer.get_seasonal_patterns()   # 'quarterly', 'monthly', 'yearly', 'seasonal_cycles'
seasonal_recs = time_analyzer.get_seasonal_recommendations()

# Text recommendations and a formatted summary
print(time_analyzer.recommendations())
print(time_analyzer.summary())
```

### Performance Scoring

```python
from src.analyzers import PerformanceScorer

scorer = PerformanceScorer(trades)

score = scorer.calculate_overall_score()
print(score.overall_score, score.letter_grade)
print(score.strengths, score.weaknesses, score.recommendations)

grade = scorer.grade_individual_trade(trades[0])
print(grade.grade, grade.score, grade.feedback)

print(scorer.grade_distribution())   # {'A': {'count': 2, 'pct': 0.5}, ...}
print(scorer.generate_performance_report())
```

### Pattern Recognition (planned)

A `PatternFinder` analyzer is planned but does not exist yet. Intended questions:
- What leads to winning trades? (e.g. win rate after winning streaks, during session overlaps)
- What leads to losing trades? (e.g. after losing streaks, Friday afternoons, weekend holds)
- Emotional patterns: revenge trades, FOMO trades, overtrading days

Time-based patterns are already available through `TimeAnalysis` above.

### AI-Powered Insights (planned)

An `LLMAnalyzer` is planned but not implemented: it would send journal statistics to an LLM and return a summary,
strengths, improvement suggestions and action items.

## 🔧 Configuration (planned)

There is no configuration file yet; `src/config/` is an empty package. A planned `config/settings.yaml` would cover
import defaults (currency, timezone, MT5 auto-sync), analysis parameters, LLM provider/model and dashboard settings.

## 🛠️ Development Roadmap

### Week 1: Core Infrastructure
- [x] Trade data model and database
- [ ] MT5/MT4 importers
- [x] CSV importer with column auto-mapping
- [x] Basic statistics calculator

### Week 2: Analysis Engine
- [x] Time-based analysis
- [ ] Pattern recognition algorithms
- [x] Drawdown and recovery analysis
- [x] Performance scoring and trade grading
- [ ] Entry/exit quality metrics

### Week 3: Dashboard
- [ ] Streamlit application scaffold
- [ ] Overview dashboard
- [ ] Trade list and details view
- [ ] Pattern visualization

### Week 4: AI Integration
- [ ] LLM analyzer implementation
- [ ] Personalized insights generation
- [ ] Improvement suggestions
- [ ] Auto-journaling prompts

### Week 5: Polish
- [ ] Additional broker imports
- [ ] Export functionality
- [ ] Documentation
- [x] Unit tests (initial pytest suite + CI)

Details in [ROADMAP.md](ROADMAP.md).

## 📤 Export Options (planned)

Not implemented yet. Planned: export trades to CSV / Excel, a PDF report, and insights to Markdown.
Today you can persist trades with `TradeDatabase` (SQLite).

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md). Priority areas:
1. MT4/MT5 and broker importers
2. New analysis metrics
3. Dashboard
4. LLM integration

## 📄 License

[MIT License](LICENSE) - Analyze your trades freely!

## ⚠️ Disclaimer

This tool is for educational and analytical purposes. Past performance does not guarantee future results.

---

**Star ⭐ if this helps you become a better trader!**
