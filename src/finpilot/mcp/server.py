import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Allow MCP server to access the service files.
SERVICES_DIR = Path(__file__).resolve().parent.parent / "services"
sys.path.append(str(SERVICES_DIR))

from statement_parser import load_and_categorize_statement
from subscription_detector import detect_subscriptions as find_subscriptions
from budget_planner import create_budget as build_budget
from adaptive_budget import create_adaptive_budget as build_adaptive_budget
from budget_history import adjust_budget as update_budget

mcp = FastMCP("FinPilot Financial Tools")

@mcp.tool()
def calculate_savings(income: float, expenses: float) -> dict:
    """Calculate savings and savings rate."""

    savings = income - expenses

    if income > 0:
        savings_rate = (savings / income) * 100
    else:
        savings_rate = 0

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "savings_rate_percent": round(savings_rate, 2),
    }

@mcp.tool()
def analyze_statement(file_path: str) -> dict:
    """Analyze a bank statement."""

    df = load_and_categorize_statement(file_path)

    income = df[
        df["type"].str.upper() == "CREDIT"
    ]["amount"].sum()

    expenses = df[
        df["type"].str.upper() == "DEBIT"
    ]["amount"].sum()

    savings = income - expenses

    if income > 0:
        savings_rate = (savings / income) * 100
    else:
        savings_rate = 0

    category_spending = (
        df[df["type"].str.upper() == "DEBIT"]
        .groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    return {
        "income": float(income),
        "expenses": float(expenses),
        "savings": float(savings),
        "savings_rate_percent": round(float(savings_rate), 2),
        "category_spending": {
            key: float(value)
            for key, value in category_spending.items()
        },
    }

@mcp.tool()
def detect_subscriptions(file_path: str) -> list:
    """Detect possible subscriptions in a bank statement."""

    result = find_subscriptions(file_path)

    return result.to_dict(orient="records")

@mcp.tool()
def create_budget(file_path: str) -> dict:
    """Create a suggested budget from a bank statement."""

    return build_budget(file_path)

@mcp.tool()
def create_adaptive_budget(file_path: str) -> dict:
    """Create an adaptive monthly budget from historical bank statement data."""

    return build_adaptive_budget(file_path)

@mcp.tool()
def adjust_budget(file_path: str) -> dict:
    """Update the budget and compare it with the previously saved budget."""

    return update_budget(file_path)

if __name__ == "__main__":
    mcp.run()