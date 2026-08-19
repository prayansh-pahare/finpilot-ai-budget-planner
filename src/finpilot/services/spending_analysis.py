import pandas as pd
import plotly.express as px

from statement_parser import load_and_categorize_statement


def calculate_category_spending(file_path: str) -> pd.DataFrame:
    statement = load_and_categorize_statement(file_path)

    expenses = statement[
        statement["type"].str.upper() == "DEBIT"
    ]

    category_totals = (
        expenses.groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    return category_totals


def create_spending_chart(file_path: str):
    category_totals = calculate_category_spending(file_path)

    chart = px.pie(
        category_totals,
        names="category",
        values="amount",
        title="FinPilot - Spending by Category"
    )

    chart.show()


if __name__ == "__main__":
    result = calculate_category_spending(
        "data/sample_statement.csv"
    )

    print(result)

    create_spending_chart(
        "data/sample_statement.csv"
    )