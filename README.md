# Stock Analysis App

A Streamlit application that retrieves historical stock prices, summarizes
performance and volatility over a selected investment window, plots adjusted
prices and drawdowns with Plotly, and asks Gemini for a cautious, evidence-based
assessment.

## What it does

- Accepts a stock ticker, a 1-month / 3-month / 6-month / 1-year window, and
  the user's stated risk tolerance.
- Fetches auto-adjusted daily price history from Yahoo Finance using `yfinance`.
- Calculates window return, annualized historical volatility, and maximum
  drawdown. The measured risk is Low at volatility up to 20%, Medium above 20%
  through 40%, and High above 40%.
- Displays adjusted closing prices and drawdown in an interactive Plotly chart.
- Sends the calculated metrics and stated risk tolerance to Gemini for a
  concise verdict. The API key is read from `GEMINI_API_KEY`.

The volatility bands are simple historical heuristics, not a forecast or a
complete measure of investment risk. Gemini's assessment is informational and
is not personalized financial advice or a guarantee of future performance.

## Setup

Use Python 3.10 or later.

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Set your Gemini API key in the process environment or create a `.env` file
   in the project directory:

   ```dotenv
   GEMINI_API_KEY=your_api_key
   ```

   Keep `.env` private; do not commit API keys.

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

The app also requires network access to Yahoo Finance and the Gemini API.

## Tests

Run the local, network-free metric tests with:

```powershell
python -m unittest test_analysis
```

`test.py` is a separate manual Gemini connectivity example; running it makes a
live API request.
