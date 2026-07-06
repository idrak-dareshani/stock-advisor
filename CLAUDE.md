# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Streamlit web app (`app.py`) that fetches stock technical indicators from Alpha Vantage's free API, charts them with matplotlib, and asks Claude (`claude-opus-4-8` via the Anthropic SDK) to produce a Buy/Hold/Sell recommendation from the summary.

## Setup & running

```bash
# Activate the existing venv (Windows)
.venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run the app (launches a local Streamlit UI)
streamlit run app.py
```

Requires a `.env` file (already present, untracked) with:
- `ANTHROPIC_API_KEY`
- `ALPHAVANTAGE_API_KEY`

There is no test suite, linter, or build step configured in this repo.

## Architecture

Everything lives in `app.py` as a linear pipeline, top to bottom:

1. **`fetch_alpha(endpoint, symbol, **params)`** — generic Alpha Vantage REST call, builds the query string and returns parsed JSON. All other fetchers go through this.
2. **`fetch_daily`**, **`fetch_indicator`** (generic for SMA/RSI/EMA), **`fetch_macd`** — each hits a specific Alpha Vantage function and normalizes the response into a DataFrame indexed by date.
3. **`get_stock_data(symbol)`** — orchestrates the fetchers, left-merges all indicator DataFrames onto the daily price DataFrame, renders a 30-day close/SMA/EMA chart to `{symbol}_chart.png` in the repo root, and builds a Markdown summary string (trend, RSI status, MACD status). Returns `{"summary", "chart"}` or `{"error"}`.
4. **`stock_agent(symbol)`** — the AI layer. Takes the summary from step 3, calls `client.messages.create(model="claude-opus-4-8", ...)` with a system prompt for a technical analysis + recommendation, and returns `(summary, chart_path, advice)` for the UI.
5. **Streamlit UI** at the bottom renders a symbol text input + analyze button; clicking it calls `stock_agent` and displays results across two tabs (Summary & Chart, AI Recommendation). Streamlit reruns the whole script top-to-bottom on every interaction — there is no persistent callback wiring like Gradio's `.click()`.

Key implementation details worth knowing before modifying:
- Alpha Vantage's free tier is rate-limited; all fetchers silently return `None`/`{"error": ...}` on missing data rather than raising, and downstream code uses `.get()` with fallbacks to avoid KeyErrors when an indicator failed to fetch.
- Chart PNGs are written to the project root using the raw ticker as the filename (e.g. `AAPL_chart.png`) and overwritten on each run — they are build artifacts, not source.
- `langchain` is in `requirements.txt` but not currently imported/used in `app.py`.
