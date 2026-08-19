from mcp.server.fastmcp import FastMCP

import pandas as pd


mcp = FastMCP("FinPilot Financial Tools")


def load_statement(file_path: str) -> pd.DataFrame:
    """Load a CSV bank statement."""
    return pd.read_csv(file_path)


@mcp.tool()
def calculate_savings(income: float, expenses: float) -> dict:
    """Calculate monthly savings and savings rate."""

    savings = income - expenses

    savings_rate = 0
    if income > 0:
        savings_rate = (savings / income) * 100

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "savings_rate_percent": round(savings_rate, 2),
    }


@mcp.tool()
def analyze_statement(file_path: str) -> dict:
    """Analyze income, expenses and category spending from a CSV bank statement."""

    df = load_statement(file_path)

    credits = df[
        df["type"].str.upper() == "CREDIT"
    ]

    debits = df[
        df["type"].str.upper() == "DEBIT"
    ]

    total_income = credits["amount"].sum()
    total_expenses = debits["amount"].sum()

    savings = total_income - total_expenses

    savings_rate = 0
    if total_income > 0:
        savings_rate = (savings / total_income) * 100

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "savings": float(savings),
        "savings_rate_percent": round(float(savings_rate), 2),
        "transaction_count": len(df),
    }


@mcp.tool()
def detect_subscriptions(file_path: str) -> list:
    """Detect possible subscriptions from known recurring merchants."""

    df = load_statement(file_path)

    known_subscriptions = [
        "NETFLIX",
        "SPOTIFY",
        "PRIME VIDEO",
        "YOUTUBE",
        "GYM",
        "ADOBE",
        "MICROSOFT",
    ]

    debits = df[
        df["type"].str.upper() == "DEBIT"
    ].copy()

    debits["description_upper"] = (
        debits["description"]
        .astype(str)
        .str.upper()
    )

    results = []

    for merchant in known_subscriptions:

        matches = debits[
            debits["description_upper"]
            .str.contains(merchant, na=False)
        ]

        if not matches.empty:
            results.append(
                {
                    "merchant": merchant,
                    "times_charged": len(matches),
                    "total_spent": float(matches["amount"].sum()),
                    "average_charge": round(
                        float(matches["amount"].mean()),
                        2,
                    ),
                }
            )

    return results


@mcp.tool()
def create_budget(file_path: str) -> dict:
    """Create a simple starting budget from a bank statement."""

    df = load_statement(file_path)

    credits = df[
        df["type"].str.upper() == "CREDIT"
    ]

    debits = df[
        df["type"].str.upper() == "DEBIT"
    ]

    total_income = float(credits["amount"].sum())
    total_expenses = float(debits["amount"].sum())

    current_savings = total_income - total_expenses

    return {
        "monthly_income": total_income,
        "current_expenses": total_expenses,
        "current_savings": current_savings,
        "suggested_needs_budget": round(total_income * 0.50, 2),
        "suggested_wants_budget": round(total_income * 0.30, 2),
        "suggested_savings_budget": round(total_income * 0.20, 2),
    }


if __name__ == "__main__":
    mcp.run()