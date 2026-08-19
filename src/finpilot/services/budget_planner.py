import pandas as pd

from statement_parser import load_and_categorize_statement


def create_budget(file_path: str) -> dict:
    statement = load_and_categorize_statement(file_path)

    # Calculate income
    income_transactions = statement[
        statement["type"].str.upper() == "CREDIT"
    ]

    total_income = income_transactions["amount"].sum()

    # Calculate expenses
    expense_transactions = statement[
        statement["type"].str.upper() == "DEBIT"
    ]

    total_expenses = expense_transactions["amount"].sum()

    # Calculate savings
    savings = total_income - total_expenses

    if total_income > 0:
        savings_rate = (savings / total_income) * 100
    else:
        savings_rate = 0

    # Suggested budget using a simple 50/30/20 starting point
    needs_budget = total_income * 0.50
    wants_budget = total_income * 0.30
    savings_budget = total_income * 0.20

    return {
        "monthly_income": round(total_income, 2),
        "current_expenses": round(total_expenses, 2),
        "current_savings": round(savings, 2),
        "current_savings_rate": round(savings_rate, 2),
        "suggested_needs_budget": round(needs_budget, 2),
        "suggested_wants_budget": round(wants_budget, 2),
        "suggested_savings_budget": round(savings_budget, 2),
    }


if __name__ == "__main__":
    budget = create_budget(
        "data/sample_statement.csv"
    )

    print("\nFinPilot Budget Analysis\n")

    for key, value in budget.items():
        print(f"{key}: {value}")