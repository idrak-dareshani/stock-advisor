# AI Quant Stock Advisor

A free, web-based financial analysis application that combines technical stock analysis with AI-powered recommendations. It leverages real-time market data and machine learning to provide actionable trading insights.

## Overview

AI Quant Stock Advisor integrates real-time market data from Alpha Vantage with OpenAI's GPT-4o to deliver professional-grade technical analysis and trading recommendations. The application features a clean, interactive web interface built with Gradio.

## Core Functionality

### Data Fetching & Technical Indicators

- **Alpha Vantage Integration**: Fetches real-time and historical stock data using the free Alpha Vantage API
- **Technical Indicators Analyzed**:
  - **SMA (Simple Moving Average)**: 20-period average to identify trends
  - **EMA (Exponential Moving Average)**: 20-period weighted average for responsiveness
  - **RSI (Relative Strength Index)**: Momentum indicator identifying overbought/oversold conditions
  - **MACD (Moving Average Convergence Divergence)**: Tracks momentum and potential trend changes
  - **Daily Price Data**: Open, High, Low, Close, and Volume

### Data Processing Pipeline

- Aggregates multiple technical indicators into a unified DataFrame
- Performs data validation and type conversion
- Sorts and indexes data by date for time-series analysis
- Gracefully handles missing data from API responses

### Technical Analysis & Visualization

- Generates 30-day price charts with overlaid indicators (Close, SMA, EMA)
- Interprets technical signals:
  - **Trend Detection**: Compares closing price against SMA
  - **RSI Status**: Categorizes as Overbought (>70), Oversold (<30), or Neutral
  - **MACD Interpretation**: Bullish if MACD > Signal line, otherwise Bearish

### AI-Powered Recommendation Engine

- Integrates **OpenAI GPT-4o** to generate professional financial analysis
- Synthesizes technical summary and provides **Buy/Hold/Sell recommendations**
- Uses system prompts to ensure factual, professional output

### User Interface

- **Interactive Web App** with clean tabbed layout
- **Input Section**: Stock symbol entry (e.g., AAPL, MSFT, TSLA)
- **Output Tabs**:
  - **📊 Summary & Chart**: Technical metrics + 30-day price chart
  - **🤖 AI Recommendation**: AI-generated analysis and trading advice
- Responsive design with custom CSS styling

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Python 3.x |
| **UI Framework** | Gradio |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib |
| **Market Data** | Alpha Vantage API (free tier) |
| **AI Model** | OpenAI GPT-4o |
| **API Requests** | Requests library |
| **Configuration** | python-dotenv |

## Key Features

✅ **Free to Use**: Leverages free-tier APIs  
✅ **Real-time Analysis**: Live market data integration  
✅ **Multi-indicator Support**: Combines 4 major technical indicators  
✅ **AI-Powered Insights**: Professional-grade recommendations  
✅ **Visual Dashboard**: Interactive charts and summaries  
✅ **Emoji-Enhanced**: User-friendly visual indicators  

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository** (or navigate to your project directory):
   ```bash
   cd stock-advisor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ALPHAVANTAGE_API_KEY=your_alphavantage_api_key_here
   ```

   - Get your **OpenAI API Key** from: https://platform.openai.com/api-keys
   - Get your **Alpha Vantage API Key** from: https://www.alphavantage.co/

## Running the Application

```bash
python app.py
```

The application will launch locally at:
```
http://127.0.0.1:7860
```

Open this URL in your browser to access the Stock Advisor interface.

## API Requirements

- **OpenAI API Key** (`OPENAI_API_KEY`) - For GPT-4o access
- **Alpha Vantage API Key** (`ALPHAVANTAGE_API_KEY`) - For stock data

Both APIs offer free tiers suitable for testing and development.

## Workflow

1. User enters stock symbol (e.g., AAPL)
2. App fetches daily OHLCV data + technical indicators from Alpha Vantage
3. Data aggregated, validated, and processed
4. 30-day chart generated with indicators
5. Technical summary calculated (trends, RSI status, MACD signal)
6. AI analyzes summary and generates Buy/Hold/Sell recommendation
7. Results displayed in tabbed interface

## Error Handling

- Validates API response structure before processing
- Returns "Unable to fetch data" message if data unavailable
- Handles missing indicator data gracefully with defaults

## Project Structure

```
stock-advisor/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # API keys (create this file)
```

## Contributing

Feel free to submit issues or pull requests to improve the application.

## Disclaimer

This application is for educational and informational purposes only. It is not intended to provide professional investment advice. Always conduct your own research and consult with a financial advisor before making investment decisions.

## License

This project is open source and available under the MIT License.
