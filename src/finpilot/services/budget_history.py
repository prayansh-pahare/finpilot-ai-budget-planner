import json
from pathlib import Path

from adaptive_budget import create_adaptive_budget

HISTORY_FILE = Path("data/budget_history.json")

def adjust_budget(file_path: str) -> dict:
    """Create a budget and compare it with the previous saved budget."""

    # Create the latest budget
    current_budget = create_adaptive_budget(file_path)
    previous_budget = None

    # Check whether an older budget exists
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as file:
            previous_budget = json.load(file)

    # Start with version 1
    version = 1
    if previous_budget:
        version = previous_budget.get("version", 0) + 1

    current_budget["version"] = version

    # ----------------------------------------
    # Compare current and previous budgets
    # ----------------------------------------
    changes = []

    if previous_budget:

        old_expenses = previous_budget.get(
            "average_monthly_expenses",
            0,
        )

        new_expenses = current_budget[
            "average_monthly_expenses"
        ]

        expense_change = new_expenses - old_expenses

        if expense_change > 0:

            changes.append(
                f"Average monthly expenses increased "
                f"by ₹{expense_change:,.2f}."
            )

        elif expense_change < 0:

            changes.append(
                f"Average monthly expenses decreased "
                f"by ₹{abs(expense_change):,.2f}."
            )

        else:

            changes.append(
                "Average monthly expenses did not change."
            )

        old_savings = previous_budget.get(
            "average_monthly_savings",
            0,
        )

        new_savings = current_budget[
            "average_monthly_savings"
        ]

        savings_change = new_savings - old_savings

        if savings_change > 0:

            changes.append(
                f"Average monthly savings improved "
                f"by ₹{savings_change:,.2f}."
            )

        elif savings_change < 0:

            changes.append(
                f"Average monthly savings decreased "
                f"by ₹{abs(savings_change):,.2f}."
            )

        else:

            changes.append(
                "Average monthly savings did not change."
            )

    else:

        changes.append(
            "This is your first saved budget."
        )

    current_budget["changes_from_previous"] = changes

    # ----------------------------------------
    # Save latest budget
    # ----------------------------------------

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(HISTORY_FILE, "w") as file:

        json.dump(
            current_budget,
            file,
            indent=4,
        )

    return current_budget


if __name__ == "__main__":

    result = adjust_budget(
        "data/sample_statement.csv"
    )

    print("\nFinPilot Continuous Budget Adjustment\n")

    print(
        "Budget Version:",
        result["version"],
    )

    print("\nChanges:")

    for change in result["changes_from_previous"]:
        print("-", change)