# 📔 TradeJournal Analyzer

> Intelligent trading journal analyzer that extracts insights from your trade history, identifies patterns, and suggests improvements.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Why This Tool?

Most traders keep journals but never analyze them properly. This tool:

- 📊 **Auto-imports** trades from MT4/MT5, brokers, or CSV
- 🔍 **Finds patterns** in your winning and losing trades
- 🧠 **AI-powered insights** using LLM analysis
- 📈 **Visualizes** your trading performance over time

## ✨ Features

### Import & Sync
- 📥 Import from MT4/MT5 history
- 📥 Import from broker statements (Interactive Brokers, TD Ameritrade)
- 📥 CSV/Excel import with smart column mapping
- 🔄 Auto-sync with MT5 (live updates)

### Analytics
- 📊 Win rate by symbol, timeframe, day of week, time of day
- 💰 Average R:R ratio and expectancy
- 📉 Drawdown analysis and recovery patterns
- 🎯 Entry accuracy (how close to optimal entry?)
- ⏱️ Holding time analysis

### Pattern Recognition
- 🔮 What conditions lead to your best trades?
- ⚠️ What patterns precede losing streaks?
- 📆 Time-based performance patterns
- 🎭 Emotional pattern detection (revenge trades, FOMO)

### AI Insights
- 🤖 LLM-powered trade review
- 💡 Personalized improvement suggestions
- 📝 Automated trade journaling prompts

## 🏗️ Project Structure

```
trade-journal-analyzer/
├── importers/
│   ├── mt5_importer.py       # MetaTrader 5 history
│   ├── mt4_importer.py       # MetaTrader 4 history  
│   ├── ib_importer.py        # Interactive Brokers
│   ├── csv_importer.py       # Generic CSV
│   └── mapper.py             # Smart column mapping
├── analyzers/
│   ├── basic_stats.py        # Win rate, PnL, etc.
│   ├── time_analysis.py      # Time-based patterns
│   ├── pattern_finder.py     # Trade pattern recognition
│   ├── drawdown.py           # Drawdown analysis
│   └── llm_analyzer.py       # AI-powered insights
├── dashboard/
│   ├── app.py                # Main Streamlit app
│   ├── pages/
│   │   ├── overview.py       # Dashboard home
│   │   ├── trades.py         # Trade list & details
│   │   ├── patterns.py       # Pattern analysis
│   │   └── insights.py       # AI insights
│   └── components/
│       ├── charts.py         # Plotly charts
│       └── filters.py        # Filter widgets
├── models/
│   ├── trade.py              # Trade data model
│   └── journal_entry.py      # Journal entry model
├── storage/
│   ├── database.py           # SQLite storage
│   └── export.py             # Export functionality
├── config/
└── tests/
```

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Caesarcph/trade-journal-analyzer.git
cd trade-journal-analyzer
pip install -r requirements.txt
```

### Import Your Trades

```bash
# From MT5
python -m importers.mt5_importer --account 12345678

# From CSV
python -m importers.csv_importer trades.csv

# From Interactive Brokers
python -m importers.ib_importer statement.xml
```

### Launch Dashboard

```bash
streamlit run dashboard/app.py
```

## 📊 Dashboard Preview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADE JOURNAL ANALYZER                        │
│                                                                  │
│  Date Range: [Jan 1, 2024] to [Dec 15, 2024]  Symbols: [All ▼]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Total   │  │   Win    │  │  Profit  │  │   Avg    │        │
│  │  Trades  │  │   Rate   │  │  Factor  │  │   R:R    │        │
│  │   247    │  │  58.3%   │  │   1.82   │  │   1.65   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  [Equity Curve Chart]                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │    📈                                              ╱     │   │
│  │         ╱╲    ╱╲                              ╱╲╱       │   │
│  │    ╱╲╱╲╱  ╲╱╲╱  ╲╱╲      ╱╲                ╱            │   │
│  │   ╱              ╲╱╲╱╲╱╲╱  ╲╱╲        ╱╲╱               │   │
│  │ ╱                              ╲    ╱                    │   │
│  │╱                                ╲╱╲╱                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Jan     Mar     May      Jul      Sep      Nov               │
│                                                                  │
│  📊 PERFORMANCE BY SYMBOL           📅 PERFORMANCE BY DAY       │
│  ┌───────────────────────┐         ┌───────────────────────┐   │
│  │ EURUSD  ████████ 62%  │         │ Mon  ████████ +$2,340 │   │
│  │ GBPUSD  ██████   54%  │         │ Tue  ██████   +$1,230 │   │
│  │ USDJPY  ███████  58%  │         │ Wed  ████████ +$2,100 │   │
│  │ XAUUSD  █████    51%  │         │ Thu  ███      +$450   │   │
│  └───────────────────────┘         │ Fri  ██       -$320   │   │
│                                    └───────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  🤖 AI INSIGHTS                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Your win rate drops 15% after a losing streak of 3+    │   │
│  │   trades. Consider taking a break after consecutive      │   │
│  │   losses.                                                │   │
│  │                                                          │   │
│  │ • Friday trades have negative expectancy (-$64/trade).   │   │
│  │   Consider avoiding trading on Fridays.                  │   │
│  │                                                          │   │
│  │ • Your best entries come within 30 mins of London open.  │   │
│  │   Focus on this session for higher quality setups.       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📈 Analytics Deep Dive

### Basic Statistics

```python
from analyzers import BasicStats

stats = BasicStats(trades)

print(f"Total Trades: {stats.total_trades}")
print(f"Win Rate: {stats.win_rate:.1%}")
print(f"Profit Factor: {stats.profit_factor:.2f}")
print(f"Average Win: ${stats.avg_win:.2f}")
print(f"Average Loss: ${stats.avg_loss:.2f}")
print(f"Expectancy: ${stats.expectancy:.2f}/trade")
print(f"Max Drawdown: {stats.max_drawdown:.1%}")
print(f"Sharpe Ratio: {stats.sharpe_ratio:.2f}")
```

### Time-Based Analysis

```python
from analyzers import TimeAnalysis

time_stats = TimeAnalysis(trades)

# Performance by day of week
day_perf = time_stats.by_day_of_week()
# {'Monday': {'win_rate': 0.62, 'pnl': 2340}, ...}

# Performance by hour
hour_perf = time_stats.by_hour()
# Best trading hours identified

# Performance by session
session_perf = time_stats.by_session()
# {'Asian': {...}, 'London': {...}, 'New York': {...}}
```

### Pattern Recognition

```python
from analyzers import PatternFinder

patterns = PatternFinder(trades)

# What leads to winning trades?
winning_patterns = patterns.find_winning_conditions()
# [
#   "Trades after 2+ winning streak: 68% win rate",
#   "Trades during London-NY overlap: 64% win rate",
#   "Trades with R:R > 2: 71% profitable when target hit"
# ]

# What leads to losing trades?
losing_patterns = patterns.find_losing_conditions()
# [
#   "Trades after 3+ losing streak: 42% win rate (revenge trading?)",
#   "Friday afternoon trades: 38% win rate",
#   "Trades held over weekend: 35% win rate"
# ]

# Emotional patterns
emotional = patterns.detect_emotional_trading()
# {
#   "revenge_trades": 12,
#   "fomo_trades": 8,
#   "overtrading_days": 5
# }
```

### Time-Based Analysis

```python
from analyzers import TimeAnalysis

time_analyzer = TimeAnalysis(trades)

# Performance by day of week
day_perf = time_analyzer.by_day_of_week()
# {'Monday': {'win_rate': 0.62, 'pnl': 2340, 'avg_pnl': 58.5}, ...}

# Performance by hour
hour_perf = time_analyzer.by_hour()
# Best trading hours identified

# Performance by trading session
session_perf = time_analyzer.by_session()
# {'Asian': {'win_rate': 0.55, 'total_trades': 20, 'avg_pnl': 25.5},
#  'London': {'win_rate': 0.68, 'total_trades': 45, 'avg_pnl': 42.3},
#  'New_York': {'win_rate': 0.61, 'total_trades': 35, 'avg_pnl': 38.7},
#  'London_NY_Overlap': {'win_rate': 0.72, 'total_trades': 28, 'avg_pnl': 51.2}}

# Performance by time period
period_perf = time_analyzer.by_period()
# {'pre_market': {...}, 'market_open': {...}, 'midday': {...}, ...}

# Get peak performance hours
peak_hours = time_analyzer.get_peak_hours(limit=5)
# [{'hour': 14, 'win_rate': 0.71, 'avg_pnl': 27.14, 'total_trades': 7}, ...]

# Get worst performing hours
worst_hours = time_analyzer.get_worst_hours(limit=3)
# [{'hour': 10, 'win_rate': 0.0, 'avg_pnl': -30.0, 'total_trades': 1}, ...]

# Get best/worst weekdays
best_weekday = time_analyzer.get_best_weekday()
# {'weekday': 1, 'name': 'Tuesday', 'win_rate': 0.68, 'avg_pnl': 42.5, ...}
worst_weekday = time_analyzer.get_worst_weekday()
# {'weekday': 4, 'name': 'Friday', 'win_rate': 0.45, 'avg_pnl': -12.3, ...}

# Get recommendations based on time patterns
recommendations = time_analyzer.recommendations()
# ["Focus on trading during 14:00 - 71.4% win rate across 7 trades",
#  "Avoid trading during 10:00 - only 0.0% win rate",
#  "Tuesday is your strongest day - schedule important trades then"]

# Get complete analysis summary
print(time_analyzer.summary())
# "⏰ TIME-BASED PATTERN ANALYSIS
#  ==================================================
#  Total Closed Trades Analyzed: 247
#  
#  🏆 BEST PERFORMING HOURS:
#   14:00 - Win Rate: 71.4% | Avg PnL: $27.14
#  
#  ⚠️ WORST PERFORMING HOURS:
#   10:00 - Win Rate: 0.0% | Avg PnL: $-30.00
#  
#  📅 DAY OF WEEK PERFORMANCE:
#    Best: Tuesday - Win Rate: 68.0% | Avg PnL: $42.50
#    Worst: Friday - Win Rate: 45.0% | Avg PnL: $-12.30
#  
#  🌍 TRADING SESSIONS:
#    London: 45 trades, Win Rate: 68.0%, Avg PnL: $42.30
#    New_York: 35 trades, Win Rate: 61.0%, Avg PnL: $38.70"
```

### AI-Powered Insights

```python
from analyzers import LLMAnalyzer

llm = LLMAnalyzer(model="claude-sonnet-4-20250514")

# Get personalized insights
insights = llm.analyze_journal(trades, depth="comprehensive")

print(insights.summary)
# "Your trading shows a clear edge in trend-following setups during
#  the London session. However, performance degrades significantly 
#  on Fridays and after losing streaks..."

print(insights.strengths)
# ["Strong risk management (avg loss < avg win * 0.5)",
#  "Excellent entry timing during London open",
#  "Consistent position sizing"]

print(insights.improvements)
# ["Consider avoiding Friday trades (-$320 net)",
#  "Implement a 2-hour break after 3 consecutive losses",
#  "Your XAUUSD edge is weak - consider paper trading only"]

print(insights.action_items)
# ["Create a pre-trade checklist for Friday trades",
#  "Set a daily loss limit of 3% to prevent overtrading",
#  "Review and update your XAUUSD strategy"]
```

## 🔧 Configuration

```yaml
# config/settings.yaml

import:
  default_currency: USD
  timezone: UTC
  auto_sync_mt5: true
  sync_interval_minutes: 5

analysis:
  min_trades_for_pattern: 20
  lookback_periods: [7, 30, 90, 365]
  
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  analysis_depth: standard  # quick, standard, comprehensive
  
dashboard:
  theme: dark
  default_date_range: 90  # days
  refresh_interval: 60  # seconds
```

## 🛠️ Development Roadmap

### Week 1: Core Infrastructure
- [x] Trade data model and database
- [ ] MT5/MT4 importers
- [ ] CSV importer with smart mapping
- [x] Basic statistics calculator

### Week 2: Analysis Engine
- [x] Time-based analysis
- [ ] Pattern recognition algorithms
- [ ] Drawdown and recovery analysis
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
- [ ] Unit tests

## 📤 Export Options

```python
from storage import Exporter

exporter = Exporter(trades)

# Export to various formats
exporter.to_csv("trades_export.csv")
exporter.to_excel("trades_export.xlsx")
exporter.to_pdf_report("monthly_report.pdf")

# Export insights
exporter.insights_to_markdown("insights.md")
```

## 🤝 Contributing

Contributions welcome! Priority areas:
1. Additional broker importers
2. New analysis metrics
3. Dashboard improvements
4. LLM prompt optimization

## 📄 License

MIT License - Analyze your trades freely!

## ⚠️ Disclaimer

This tool is for educational and analytical purposes. Past performance does not guarantee future results.

---

**Star ⭐ if this helps you become a better trader!**
