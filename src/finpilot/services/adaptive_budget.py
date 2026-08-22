import pandas as pd
from statement_parser import load_and_categorize_statement

def create_adaptive_budget(file_path: str) -> dict:
    """Create an adaptive monthly budget based on historical spending."""

    # -------------------------------------------------
    # 1. Load and categorize the bank statement
    # -------------------------------------------------

    statement = load_and_categorize_statement(file_path)

    # Convert the date column into real dates
    statement["date"] = pd.to_datetime(statement["date"])

    # -------------------------------------------------
    # 2. Find how many months are in the statement
    # -------------------------------------------------

    number_of_months = (
        statement["date"]
        .dt.to_period("M")
        .nunique()
    )

    if number_of_months == 0:
        number_of_months = 1

    # -------------------------------------------------
    # 3. Calculate average monthly income
    # -------------------------------------------------

    income_transactions = statement[
        statement["type"].str.upper() == "CREDIT"
    ]

    total_income = float(
        income_transactions["amount"].sum()
    )

    average_monthly_income = (
        total_income / number_of_months
    )

    # -------------------------------------------------
    # 4. Calculate average monthly expenses
    # -------------------------------------------------

    expense_transactions = statement[
        statement["type"].str.upper() == "DEBIT"
    ]

    total_expenses = float(
        expense_transactions["amount"].sum()
    )

    average_monthly_expenses = (
        total_expenses / number_of_months
    )

    # -------------------------------------------------
    # 5. Calculate average monthly savings
    # -------------------------------------------------

    average_monthly_savings = (
        average_monthly_income
        - average_monthly_expenses
    )

    # -------------------------------------------------
    # 6. Create starting 50/30/20 targets
    # -------------------------------------------------

    needs_target = average_monthly_income * 0.50

    wants_target = average_monthly_income * 0.30

    savings_target = average_monthly_income * 0.20

    # -------------------------------------------------
    # 7. Calculate the savings gap
    # -------------------------------------------------

    savings_gap = (
        savings_target
        - average_monthly_savings
    )

    # -------------------------------------------------
    # 8. Calculate average spending by category
    # -------------------------------------------------

    category_totals = (
        expense_transactions
        .groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    average_category_spending = {
        category: round(
            float(amount) / number_of_months,
            2,
        )
        for category, amount
        in category_totals.items()
    }

    # -------------------------------------------------
    # 9. Categories FinPilot may suggest reducing
    # -------------------------------------------------

    adjustable_categories = {
        "Food",
        "Shopping",
        "Entertainment",
        "Transport",
        "Health & Fitness",
    }

    adjustment_suggestions = []

    # -------------------------------------------------
    # 10. Suggest reductions only when savings
    #     are below the target
    # -------------------------------------------------

    if savings_gap > 0:

        adjustable_spending = {
            category: amount
            for category, amount
            in average_category_spending.items()
            if category in adjustable_categories
        }

        total_adjustable_spending = sum(
            adjustable_spending.values()
        )

        if total_adjustable_spending > 0:

            for category, amount in (
                adjustable_spending.items()
            ):

                # Find this category's share
                # of adjustable spending
                share = (
                    amount
                    / total_adjustable_spending
                )

                # Calculate how much FinPilot
                # suggests reducing
                suggested_reduction = min(
                    savings_gap * share,
                    amount,
                )

                # Do not allow a negative target
                new_target = max(
                    amount - suggested_reduction,
                    0,
                )

                adjustment_suggestions.append(
                    {
                        "category": category,

                        "current_average": round(
                            amount,
                            2,
                        ),

                        "suggested_reduction": round(
                            suggested_reduction,
                            2,
                        ),

                        "new_target": round(
                            new_target,
                            2,
                        ),
                    }
                )

    # -------------------------------------------------
    # 11. Return the complete adaptive budget
    # -------------------------------------------------

    return {
        "months_analyzed": int(
            number_of_months
        ),

        "average_monthly_income": round(
            average_monthly_income,
            2,
        ),

        "average_monthly_expenses": round(
            average_monthly_expenses,
            2,
        ),

        "average_monthly_savings": round(
            average_monthly_savings,
            2,
        ),

        "targets": {
            "needs": round(
                needs_target,
                2,
            ),

            "wants": round(
                wants_target,
                2,
            ),

            "savings": round(
                savings_target,
                2,
            ),
        },

        "savings_target": round(
            savings_target,
            2,
        ),

        "savings_gap": round(
            savings_gap,
            2,
        ),

        "on_track": savings_gap <= 0,

        "average_category_spending":
            average_category_spending,

        "adjustment_suggestions":
            adjustment_suggestions,
    }


# -------------------------------------------------
# Test the adaptive budget planner
# -------------------------------------------------

if __name__ == "__main__":

    result = create_adaptive_budget(
        "data/sample_statement.csv"
    )

    print("\nFinPilot Adaptive Monthly Budget\n")

    print(
        "Months analyzed:",
        result["months_analyzed"],
    )

    print(
        "Average monthly income:",
        result["average_monthly_income"],
    )

    print(
        "Average monthly expenses:",
        result["average_monthly_expenses"],
    )

    print(
        "Average monthly savings:",
        result["average_monthly_savings"],
    )

    print("\nBudget Targets:")

    print(
        result["targets"]
    )

    print("\nAverage Monthly Category Spending:")

    for category, amount in (
        result["average_category_spending"].items()
    ):
        print(
            f"{category}: {amount}"
        )

    print("\nSavings Target:")

    print(
        result["savings_target"]
    )

    print("\nSavings Gap:")

    print(
        result["savings_gap"]
    )

    print("\nOn Track:")

    print(
        result["on_track"]
    )

    print("\nAdjustment Suggestions:")

    if result["adjustment_suggestions"]:

        for suggestion in (
            result["adjustment_suggestions"]
        ):
            print(suggestion)

    else:

        print(
            "No spending reductions are required "
            "to meet the current savings target."
        )