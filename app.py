import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from analysis import (
    AnalysisError,
    calculate_risk_metrics,
    fetch_stock_data,
    generate_investment_verdict,
)

st.set_page_config(
    page_title="Stock Analysis App",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
st.title("Stock Analysis App")
st.write(
    "Explore historical price performance and risk. Gemini provides an "
    "evidence-based summary, not personalized financial advice."
)

periods = {
    "1 month": "1mo",
    "3 months": "3mo",
    "6 months": "6mo",
    "1 year": "1y",
}

with st.form("investment_analysis"):
    symbol = st.text_input("Stock symbol", placeholder="AAPL").strip().upper()
    period_label = st.selectbox("Investment window", list(periods))
    risk_tolerance = st.selectbox(
        "Your risk tolerance",
        ["Low", "Medium", "High"],
    )
    submitted = st.form_submit_button("Analyze investment")

if submitted:
    if not symbol:
        st.error("Enter a stock symbol to analyze.")
        st.stop()

    period = periods[period_label]
    try:
        with st.spinner("Fetching market data and generating the analysis..."):
            history = fetch_stock_data(symbol, period)
            metrics = calculate_risk_metrics(
                history,
                symbol=symbol,
                period=period,
                risk_tolerance=risk_tolerance,
            )
            verdict = generate_investment_verdict(metrics)
    except AnalysisError as error:
        st.error(str(error))
        st.stop()

    st.subheader(f"{metrics.symbol} — {period_label}")
    first, second, third, fourth = st.columns(4)
    first.metric("Window return", f"{metrics.total_return:.2%}")
    second.metric("Annualized volatility", f"{metrics.annualized_volatility:.2%}")
    third.metric("Maximum drawdown", f"{metrics.max_drawdown:.2%}")
    fourth.metric("Measured risk", metrics.risk_level)
    st.caption(f"Your selected risk tolerance: {metrics.risk_tolerance}")

    close = history["Close"]
    if getattr(close, "ndim", 1) == 2:
        close = close.iloc[:, 0]
    drawdown = close / close.cummax() - 1

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=("Adjusted closing price", "Drawdown"),
    )
    figure.add_trace(
        go.Scatter(x=close.index, y=close, mode="lines", name="Adjusted close"),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown,
            mode="lines",
            name="Drawdown",
            fill="tozeroy",
        ),
        row=2,
        col=1,
    )
    figure.update_yaxes(title_text="Price", row=1, col=1)
    figure.update_yaxes(title_text="Drawdown", tickformat=".0%", row=2, col=1)
    figure.update_layout(height=600, showlegend=False)
    st.plotly_chart(figure, use_container_width=True)

    st.subheader("Gemini's assessment")
    st.markdown(verdict)
    st.caption(
        "This is an informational summary based on the selected historical window, "
        "not a guarantee or a personalized recommendation."
    )
