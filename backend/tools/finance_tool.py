from langchain.tools import tool
import yfinance as yf

@tool
def finance_tool(ticker: str) -> str:
    """
    Fetches real-time financial data for a given stock or crypto ticker symbol.
    Provide the exact ticker symbol (e.g., 'AAPL', 'MSFT', 'BTC-USD', 'ETH-USD').
    Use this to answer questions about stock price, crypto tracking, and company value!
    """
    try:
        data = yf.Ticker(ticker)
        info = data.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        currency = info.get('currency', 'USD')
        day_high = info.get('dayHigh', 'N/A')
        day_low = info.get('dayLow', 'N/A')
        summary = info.get('longBusinessSummary', 'No summary available.')[:500]
        
        return f"**Ticker: {ticker.upper()}**\n- **Current Price:** {current_price} {currency}\n- **Day High:** {day_high}\n- **Day Low:** {day_low}\n\n**Company/Crypto Summary:**\n{summary}..."
    except Exception as e:
        return f"Could not fetch data for ticker {ticker}. Make sure the ticker symbol is exact! Error: {e}"
