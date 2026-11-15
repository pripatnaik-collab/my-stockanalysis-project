import math
import os
from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

Period = Literal["1mo", "3mo", "6mo", "1y"]
RiskTolerance = Literal["Low", "Medium", "High"]
SUPPORTED_PERIODS = {"1mo", "3mo", "6mo", "1y"}
SUPPORTED_TOLERANCES = {"Low", "Medium", "High"}


class AnalysisError(Exception):
    """An expected issue that prevents investment analysis from completing."""


@dataclass(frozen=True)
class RiskMetrics:
    symbol: str
    period: str
    start_date: str
    end_date: str
    starting_price: float
    ending_price: float
    total_return: float
    annualized_volatility: float
    max_drawdown: float
    risk_level: str
    risk_tolerance: str


def fetch_stock_data(symbol: str, period: Period) -> pd.DataFrame:
    """Fetch auto-adjusted daily price history from Yahoo Finance."""
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise AnalysisError("Enter a stock symbol to analyze.")
    if period not in SUPPORTED_PERIODS:
        raise AnalysisError(f"Unsupported investment window: {period}")

    history = yf.Ticker(normalized_symbol).history(
        period=period,
        auto_adjust=True,
    )
    if history.empty or "Close" not in history:
        raise AnalysisError(
            f"No price history was found for {normalized_symbol}. "
            "Check the symbol and try again."
        )
    return history


def calculate_risk_metrics(
    history: pd.DataFrame,
    symbol: str,
    period: Period,
    risk_tolerance: RiskTolerance,
) -> RiskMetrics:
    """Calculate historical performance and volatility-based risk indicators."""
    if period not in SUPPORTED_PERIODS:
        raise AnalysisError(f"Unsupported investment window: {period}")
    if risk_tolerance not in SUPPORTED_TOLERANCES:
        raise AnalysisError(f"Unsupported risk tolerance: {risk_tolerance}")
    if "Close" not in history:
        raise AnalysisError("Price history is missing its closing-price data.")

    close = history["Close"]
    if isinstance(close, pd.DataFrame):
        if close.shape[1] != 1:
            raise AnalysisError("Price history contains ambiguous closing prices.")
        close = close.iloc[:, 0]
    close = pd.to_numeric(close, errors="coerce").dropna()
    if len(close) < 3 or (close <= 0).any():
        raise AnalysisError(
            "At least three valid, positive daily closing prices are required "
            "to assess risk."
        )

    daily_returns = close.pct_change().dropna()
    annualized_volatility = float(daily_returns.std(ddof=1) * math.sqrt(252))
    max_drawdown = float((close / close.cummax() - 1).min())
    if not math.isfinite(annualized_volatility) or not math.isfinite(max_drawdown):
        raise AnalysisError("The available price history could not be analyzed.")

    if annualized_volatility <= 0.20:
        risk_level = "Low"
    elif annualized_volatility <= 0.40:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return RiskMetrics(
        symbol=symbol.strip().upper(),
        period=period,
        start_date=close.index[0].strftime("%Y-%m-%d"),
        end_date=close.index[-1].strftime("%Y-%m-%d"),
        starting_price=float(close.iloc[0]),
        ending_price=float(close.iloc[-1]),
        total_return=float(close.iloc[-1] / close.iloc[0] - 1),
        annualized_volatility=annualized_volatility,
        max_drawdown=max_drawdown,
        risk_level=risk_level,
        risk_tolerance=risk_tolerance,
    )


def generate_investment_verdict(metrics: RiskMetrics) -> str:
    """Ask Gemini for a cautious verdict grounded in the calculated metrics."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AnalysisError(
            "GEMINI_API_KEY is not set. Add it to your environment or .env file "
            "to request Gemini's verdict."
        )

    model = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=0.2,
    )
    prompt = (
        "Assess this stock using only the supplied historical data. Do not invent "
        "facts, imply certainty, or treat past performance as a forecast. Compare "
        "the measured risk with the user's stated risk tolerance. Start with one "
        "clear label: INVEST, DO NOT INVEST, or INSUFFICIENT DATA. Explain the "
        "main supporting evidence, key uncertainty, and why this is not "
        "personalized financial advice. Keep the answer concise.\n\n"
        f"Historical metrics: {asdict(metrics)}"
    )
    response = model.invoke(prompt)
    content = response.content
    if isinstance(content, str):
        verdict = content.strip()
    elif isinstance(content, list):
        verdict = "\n".join(
            str(part["text"])
            for part in content
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ).strip()
    else:
        verdict = ""
    if not verdict:
        raise AnalysisError("Gemini returned an empty investment assessment.")
    return verdict
