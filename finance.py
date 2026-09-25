"""Core math for the fee-drag calculator.

Kept separate from the Streamlit UI on purpose: pure functions are easy to
test, easy to reuse, and easy to read. The UI (app.py) only handles inputs
and charts — every dollar figure comes from here.
"""

import numpy as np


def project_growth(start, monthly_contrib, gross_annual_return, mer, years):
    """Project a portfolio month by month.

    Each month, in order:
      1. the balance grows at the gross market return,
      2. the fund takes its cut (MER / 12 of the balance),
      3. your monthly contribution lands.

    Returns two arrays of length months + 1 (starting at month 0):
      balances       - portfolio value at each month end
      cumulative_fees - total fees skimmed up to each month end
    """
    months = int(years * 12)
    monthly_gross = (1 + gross_annual_return) ** (1 / 12) - 1  # annual -> monthly
    monthly_mer = mer / 12

    balances = np.zeros(months + 1)
    cum_fees = np.zeros(months + 1)
    balance = float(start)
    balances[0] = balance

    for m in range(1, months + 1):
        fee = balance * monthly_mer
        balance = balance * (1 + monthly_gross) - fee + monthly_contrib
        balances[m] = balance
        cum_fees[m] = cum_fees[m - 1] + fee

    return balances, cum_fees


def fmt_dollars(x):
    """$1,234,567 — no cents, this is a big-picture tool."""
    return f"${x:,.0f}"
