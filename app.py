import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# === Load API keys ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ALPHA_KEY = os.getenv("ALPHAVANTAGE_API_KEY")


# === Utility: Fetch and parse ===
def fetch_alpha(endpoint, symbol, **params):
    url = f"https://www.alphavantage.co/query?function={endpoint}&symbol={symbol.upper()}&apikey={ALPHA_KEY}"
    if params:
        q = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}&{q}"
    resp = requests.get(url).json()
    return resp


# === Base price ===
def fetch_daily(symbol: str):
    data = fetch_alpha("TIME_SERIES_DAILY", symbol)
    if "Time Series (Daily)" not in data:
        return None
    df = pd.DataFrame(data["Time Series (Daily)"]).T
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


# === SMA / RSI / EMA / MACD ===
def fetch_indicator(symbol, func, key):
    data = fetch_alpha(func, symbol, interval="daily", series_type="close", time_period=20)
    if key not in data:
        return None
    df = pd.DataFrame(data[key]).T
    col_name = list(df.columns)[0]
    df.columns = [col_name.upper()]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def fetch_macd(symbol):
    data = fetch_alpha("MACD", symbol, interval="daily", series_type="close")
    if "Technical Analysis: MACD" not in data:
        return None
    df = pd.DataFrame(data["Technical Analysis: MACD"]).T
    df.columns = [c.upper() for c in df.columns]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


# === Aggregate Data ===
def get_stock_data(symbol: str):
    daily = fetch_daily(symbol)
    if daily is None:
        return {"error": f"No data for {symbol}"}

    sma = fetch_indicator(symbol, "SMA", "Technical Analysis: SMA")
    rsi = fetch_indicator(symbol, "RSI", "Technical Analysis: RSI")
    ema = fetch_indicator(symbol, "EMA", "Technical Analysis: EMA")
    macd = fetch_macd(symbol)

    df = daily.copy()
    for ind in [sma, rsi, ema, macd]:
        if ind is not None:
            df = df.merge(ind, left_index=True, right_index=True, how="left")

    recent = df.tail(30)
    last = df.iloc[-1]

    trend = "Uptrend 📈" if last["close"] > last.get("SMA", last["close"]) else "Downtrend 📉"

    # === Plot ===
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(recent.index, recent["close"], label="Close", linewidth=2)
    if "SMA" in recent:
        ax.plot(recent.index, recent["SMA"], linestyle="--", label="SMA(20)")
    if "EMA" in recent:
        ax.plot(recent.index, recent["EMA"], linestyle=":", label="EMA(20)")
    ax.set_title(f"{symbol.upper()} - Close, SMA, EMA (30 Days)")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart_path = f"{symbol}_chart.png"
    plt.savefig(chart_path)
    plt.close(fig)

    # RSI
    rsi_val = last.get("RSI", None)
    if rsi_val is None:
        rsi_status = "Unavailable"
    elif rsi_val > 70:
        rsi_status = f"{rsi_val:.1f} (Overbought ⚠️)"
    elif rsi_val < 30:
        rsi_status = f"{rsi_val:.1f} (Oversold 💰)"
    else:
        rsi_status = f"{rsi_val:.1f} (Neutral ⚖️)"

    macd_val = last.get("MACD", 0)
    macd_signal = last.get("MACD_SIGNAL", 0)
    macd_status = (
        "Bullish 📈" if macd_val > macd_signal else "Bearish 📉"
    ) if "MACD_SIGNAL" in df.columns else "N/A"

    summary = (
        f"📊 **{symbol.upper()} Technical Summary**\n"
        f"- Date: {df.index[-1].date()}\n"
        f"- Close: ${last['close']:.2f}\n"
        f"- SMA(20): ${last.get('SMA', 0):.2f}\n"
        f"- EMA(20): ${last.get('EMA', 0):.2f}\n"
        f"- RSI(14): {rsi_status}\n"
        f"- MACD: {macd_status}\n"
        f"- 5-day Trend: {trend}"
    )

    return {"summary": summary, "chart": chart_path}


# === AI layer ===
def stock_agent(symbol):
    result = get_stock_data(symbol)
    if "error" in result:
        return result["error"], None, "❌ Unable to fetch data."

    prompt = f"""
You are a financial analyst. Using the following summary, analyze the short-term technical outlook.
Base your reasoning on SMA, EMA, RSI, and MACD. Conclude with a Buy / Hold / Sell recommendation.

{result['summary']}
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional financial advisor who writes concise, factual analyses."},
            {"role": "user", "content": prompt},
        ],
    )
    advice = completion.choices[0].message.content
    return result["summary"], result["chart"], advice


# === Gradio UI ===
with gr.Blocks(title="AI Quant Stock Advisor (Free)") as demo:
    gr.Markdown(
        """
        <h1 style='text-align:center'>📈 AI Quant Stock Advisor (Free API)</h1>
        <p style='text-align:center'>
        Technical analysis with SMA, EMA, RSI & MACD via Alpha Vantage (free tier)
        </p>
        """
    )

    # Properly aligned input + button
    with gr.Row(elem_id="input-row"):
        symbol_input = gr.Textbox(
            label="Stock Symbol",
            placeholder="Enter e.g., AAPL  MSFT  TSLA",
            scale=4
        )
        analyze_btn = gr.Button("🔍 Analyze", variant="primary", scale=1)

    with gr.Tabs():
        with gr.TabItem("📊 Summary & Chart"):
            summary_box = gr.Markdown()
            chart_image = gr.Image(label="Price Chart (30 Days)")

        with gr.TabItem("🤖 AI Recommendation"):
            ai_advice = gr.Markdown()

    analyze_btn.click(stock_agent, inputs=symbol_input, outputs=[summary_box, chart_image, ai_advice])

# Optional CSS tweak for alignment
demo.css = """
#input-row { align-items: center; margin-top: 10px; margin-bottom: 10px; }
"""

# When deploying on Render or similar platforms bind to 0.0.0.0 and use the PORT env var
port = int(os.getenv("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port, share=False)
