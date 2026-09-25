"""The True Cost of Fees — a Canadian MER fee-drag calculator.

Run locally with:  streamlit run app.py
Deploy free at:     https://share.streamlit.io  (see README.md)
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from finance import project_growth, fmt_dollars

# ----------------------------------------------------------------------------
# Page setup — must be the first Streamlit call in the script.
# ----------------------------------------------------------------------------
st.set_page_config(page_title="The True Cost of Fees", page_icon="💸", layout="wide")

st.title("The True Cost of Fees")
st.markdown(
    "The same market return, two different fund fees — watch the gap compound. "
    "Built for Canadian investors: many bank mutual funds charge ~2% a year, "
    "while broad-market index ETFs charge ~0.2%."
)

# ----------------------------------------------------------------------------
# Sidebar: every input lives here. Streamlit re-runs this whole script
# top-to-bottom whenever any input changes — that's the whole "framework".
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Your plan")
    start = st.number_input("Starting balance ($)", min_value=0, value=10_000, step=1_000)
    monthly = st.number_input("Monthly contribution ($)", min_value=0, value=500, step=50)
    gross = st.slider("Expected annual return, before fees (%)", 1.0, 12.0, 7.0, 0.25) / 100
    years = st.slider("Years invested", 1, 50, 30)

    st.header("Fund A")
    name_a = st.text_input("Fund A name", "Big-bank mutual fund")
    mer_a = st.number_input("Fund A MER (%)", 0.0, 3.0, 2.00, 0.05) / 100

    st.header("Fund B")
    name_b = st.text_input("Fund B name", "DIY index ETF")
    mer_b = st.number_input("Fund B MER (%)", 0.0, 3.0, 0.20, 0.05) / 100

# ----------------------------------------------------------------------------
# Run the numbers (all math lives in finance.py).
# ----------------------------------------------------------------------------
bal_a, fees_a = project_growth(start, monthly, gross, mer_a, years)
bal_b, fees_b = project_growth(start, monthly, gross, mer_b, years)

final_a, final_b = bal_a[-1], bal_b[-1]
total_paid_in = start + monthly * years * 12
extra_cost = abs(final_a - final_b)
best_final = max(final_a, final_b)

# Figure out which fund is the expensive one so the headline is always right,
# even if the user swaps the MERs around.
if mer_a > mer_b:
    exp_name, exp_mer, cheap_name, cheap_mer = name_a, mer_a, name_b, mer_b
else:
    exp_name, exp_mer, cheap_name, cheap_mer = name_b, mer_b, name_a, mer_a

# ----------------------------------------------------------------------------
# Headline + key stats.
# ----------------------------------------------------------------------------
if mer_a == mer_b:
    st.subheader("Same MER, same result — try raising one fund's fee.")
else:
    st.subheader(
        f"Over {years} years, the {exp_mer:.2%} fund ({exp_name}) leaves you "
        f"**{fmt_dollars(extra_cost)}** poorer than the {cheap_mer:.2%} fund ({cheap_name})."
    )

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{name_a} ({mer_a:.2%})", fmt_dollars(final_a))
c2.metric(f"{name_b} ({mer_b:.2%})", fmt_dollars(final_b))
c3.metric("Extra cost of the pricier fund", fmt_dollars(extra_cost))
c4.metric("You paid in", fmt_dollars(total_paid_in))

if best_final > 0 and mer_a != mer_b:
    st.info(
        f"Fees consumed **{extra_cost / best_final:.1%}** of the wealth the cheaper "
        f"fund would have built. Same market, same contributions — the only "
        f"difference is the MER."
    )

# ----------------------------------------------------------------------------
# Charts. x-axis is years; Plotly gives hover tooltips for free.
# ----------------------------------------------------------------------------
x_years = np.arange(len(bal_a)) / 12

tab1, tab2 = st.tabs(["Portfolio growth", "Fees paid"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_years, y=bal_a, name=f"{name_a} ({mer_a:.2%})",
        line=dict(color="#c0392b", width=2.5)))
    fig.add_trace(go.Scatter(
        x=x_years, y=bal_b, name=f"{name_b} ({mer_b:.2%})",
        line=dict(color="#1e7e4d", width=2.5)))
    fig.update_layout(
        xaxis_title="Years", yaxis_title="Portfolio value",
        yaxis_tickprefix="$", hovermode="x unified",
        legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")

with tab2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=x_years, y=fees_a, name=f"{name_a} fees",
        fill="tozeroy", line=dict(color="#c0392b")))
    fig2.add_trace(go.Scatter(
        x=x_years, y=fees_b, name=f"{name_b} fees",
        fill="tozeroy", line=dict(color="#1e7e4d")))
    fig2.update_layout(
        xaxis_title="Years", yaxis_title="Cumulative fees paid",
        yaxis_tickprefix="$", hovermode="x unified",
        legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig2, width="stretch")
    st.caption(
        f"{name_a} skimmed {fmt_dollars(fees_a[-1])} in total; "
        f"{name_b} skimmed {fmt_dollars(fees_b[-1])}."
    )

# ----------------------------------------------------------------------------
# Honest fine print — every model has assumptions, say them out loud.
# ----------------------------------------------------------------------------
with st.expander("Assumptions & limitations"):
    st.markdown(
        "- MER is deducted monthly as MER ÷ 12, a standard approximation.\n"
        "- Returns are constant and *before* fees. Real markets bounce around; "
        "the long-run gap is what matters here, not any single year.\n"
        "- Ignores inflation, taxes, trading commissions, and fund switching costs.\n"
        "- Illustrative only — not financial advice."
    )

st.caption("Built with Python + Streamlit · github.com/your-username/mer-fee-calculator")
