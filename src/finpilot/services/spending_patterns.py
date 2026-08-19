import pandas as pd
import plotly.express as px

from statement_parser import load_and_categorize_statement


def calculate_daily_spending(file_path: str) -> pd.DataFrame:
    statement = load_and_categorize_statement(file_path)

    expenses = statement[
        statement["type"].str.upper() == "DEBIT"
    ].copy()

    expenses["date"] = pd.to_datetime(expenses["date"])

    daily_spending = (
        expenses.groupby("date")["amount"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    return daily_spending


def create_spending_trend_chart(file_path: str):
    daily_spending = calculate_daily_spending(file_path)

    chart = px.line(
        daily_spending,
        x="date",
        y="amount",
        markers=True,
        title="FinPilot - Daily Spending Trend"
    )

    chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount Spent"
    )

    chart.show()


if __name__ == "__main__":
    result = calculate_daily_spending(
        "data/sample_statement.csv"
    )

    print(result)

    create_spending_trend_chart(
        "data/sample_statement.csv"
    )