# Roadmap

## Implemented

- `Trade` data model (`src/models/trade.py`) and SQLite storage (`src/storage/database.py`)
- CSV / Excel import with header auto-mapping and order-type normalization (`src/importers/csv_importer.py`)
- Analyzers (`src/analyzers/`): basic statistics, drawdown, time-based patterns (hour, weekday, month,
  session, session overlap, period, seasonality, time-based risk metrics), performance scorer and trade grades
- pytest suite in `tests/` and GitHub Actions CI

## Planned

### Import & sync
- MT5 history importer and MT4 history importer
- Broker statement importers (Interactive Brokers, TD Ameritrade)
- Auto-sync with a running MT5 terminal
- Command-line entry points for importers

### Analysis
- Pattern recognition (`PatternFinder`): winning / losing conditions, losing-streak precursors
- Emotional pattern detection (revenge trades, FOMO, overtrading)
- Entry/exit quality metrics (entry accuracy)
- Win rate by timeframe (needs a timeframe field on `Trade`)

### AI insights
- `LLMAnalyzer`: LLM-powered trade review, personalized suggestions, auto-journaling prompts

### Dashboard
- Streamlit app: overview, trade list/details, pattern and insight pages, Plotly charts, filters

### Storage, export & config
- Journal entry model
- Export to CSV / Excel / PDF report / Markdown insights
- `config/settings.yaml` for import, analysis, LLM and dashboard settings

### Quality
- Broader test coverage (importers, storage, edge cases)
- Documentation
