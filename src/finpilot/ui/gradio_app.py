import gradio as gr
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path


# -------------------------------------------------
# Allow Gradio to access our service and agent files
# -------------------------------------------------

FINPILOT_DIR = Path(__file__).resolve().parent.parent

SERVICES_DIR = FINPILOT_DIR / "services"
AGENTS_DIR = FINPILOT_DIR / "agents"

sys.path.append(str(SERVICES_DIR))
sys.path.append(str(AGENTS_DIR))


# -------------------------------------------------
# Import our existing FinPilot features
# -------------------------------------------------

from statement_parser import load_and_categorize_statement

from subscription_detector import detect_subscriptions

from spending_patterns import calculate_daily_spending

from adaptive_budget import create_adaptive_budget

from finance_agent import run_finpilot


# -------------------------------------------------
# Main Gradio function
# -------------------------------------------------

def analyze_finances(statement, user_message):
    """
    Analyze an uploaded bank statement and optionally
    ask the FinPilot AI financial agent a question.
    """

    # ---------------------------------------------
    # No input
    # ---------------------------------------------

    if statement is None and not user_message:

        return (
            "₹0",
            "₹0",
            "₹0",
            "0%",
            None,
            None,
            pd.DataFrame(),
            "",
            "Please upload a bank statement or enter a message.",
        )

    # Default values
    income_text = "₹0"
    expenses_text = "₹0"
    savings_text = "₹0"
    savings_rate_text = "0%"

    spending_chart = None
    trend_chart = None

    subscriptions_table = pd.DataFrame()

    budget_summary = ""

    ai_response = ""

    # ---------------------------------------------
    # Bank statement analysis
    # ---------------------------------------------

    if statement is not None:
        try:
            df = load_and_categorize_statement(statement)
        except Exception as error:
            return (
                "₹0",
                "₹0",
                "₹0",
                "0%",
                None,
                None,
                pd.DataFrame(),
                "",
                (
                    "FinPilot could not read this bank statement.\n\n"
                    "Please make sure you uploaded a valid CSV file "
                    "with these columns:\n\n"
                    "date, description, amount, type\n\n"
                    f"Technical details: {error}"
                ),
            )

        # -------------------------
        # Income
        # -------------------------

        income = df[
            df["type"].str.upper() == "CREDIT"
        ]["amount"].sum()

        # -------------------------
        # Expenses
        # -------------------------

        expenses = df[
            df["type"].str.upper() == "DEBIT"
        ]["amount"].sum()

        # -------------------------
        # Savings
        # -------------------------

        savings = income - expenses

        if income > 0:
            savings_rate = (
                savings / income
            ) * 100
        else:
            savings_rate = 0

        income_text = f"₹{income:,.2f}"
        expenses_text = f"₹{expenses:,.2f}"
        savings_text = f"₹{savings:,.2f}"
        savings_rate_text = f"{savings_rate:.2f}%"

        # -----------------------------------------
        # Spending by category chart
        # -----------------------------------------

        expense_df = df[
            df["type"].str.upper() == "DEBIT"
        ]

        category_totals = (
            expense_df
            .groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        spending_chart = px.pie(
            category_totals,
            names="category",
            values="amount",
            title="Spending by Category",
        )

        # -----------------------------------------
        # Spending trend chart
        # -----------------------------------------

        daily_spending = calculate_daily_spending(
            statement
        )

        trend_chart = px.line(
            daily_spending,
            x="date",
            y="amount",
            markers=True,
            title="Daily Spending Trend",
        )

        trend_chart.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount Spent",
        )

        # -----------------------------------------
        # Subscription detection
        # -----------------------------------------

        subscriptions_table = detect_subscriptions(
            statement
        )

        # -----------------------------------------
        # Adaptive budget
        # -----------------------------------------

        budget = create_adaptive_budget(
            statement
        )

        budget_summary = (
            f"Months analyzed: "
            f"{budget['months_analyzed']}\n\n"

            f"Average monthly income: "
            f"₹{budget['average_monthly_income']:,.2f}\n"

            f"Average monthly expenses: "
            f"₹{budget['average_monthly_expenses']:,.2f}\n"

            f"Average monthly savings: "
            f"₹{budget['average_monthly_savings']:,.2f}\n\n"

            f"Savings target: "
            f"₹{budget['savings_target']:,.2f}\n"

            f"On track: "
            f"{budget['on_track']}"
        )

        if budget["adjustment_suggestions"]:

            budget_summary += (
                "\n\nSuggested Adjustments:\n"
            )

            for suggestion in (
                budget["adjustment_suggestions"]
            ):

                budget_summary += (
                    f"\n• {suggestion['category']}: "
                    f"reduce by approximately "
                    f"₹{suggestion['suggested_reduction']:,.2f}"
                )

        else:

            budget_summary += (
                "\n\nNo spending reductions are required "
                "to meet the current savings target."
            )

    # ---------------------------------------------
    # FinPilot AI Agent
    # ---------------------------------------------

    if user_message:

        ai_response = run_finpilot(
            user_message,
            statement,
        )

    elif statement is not None:

        ai_response = (
            "Your bank statement has been analyzed. "
            "You can now ask FinPilot a financial question "
            "using the text box above."
        )

    # ---------------------------------------------
    # Return everything to Gradio
    # ---------------------------------------------

    return (
        income_text,
        expenses_text,
        savings_text,
        savings_rate_text,
        spending_chart,
        trend_chart,
        subscriptions_table,
        budget_summary,
        ai_response,
    )


# -------------------------------------------------
# Gradio Interface
# -------------------------------------------------

with gr.Blocks(
    title="FinPilot AI Budget Planner"
) as app:

    gr.Markdown(
        """
        # 💰 FinPilot AI Budget Planner

        ### Your Agentic AI Personal Finance Assistant

        Upload your bank statement and let FinPilot analyze
        your spending, subscriptions, savings and budget.

        You can also ask financial questions in simple language.
        """
    )

    # -------------------------------------------------
    # Input section
    # -------------------------------------------------

    with gr.Row():

        statement_input = gr.File(
            label="Upload Bank Statement",
            file_types=[".csv"],
            type="filepath",
        )

        text_input = gr.Textbox(
            label="Ask FinPilot",
            placeholder=(
                "Example: Analyze my spending and tell me "
                "how I can save more money."
            ),
            lines=5,
        )

    analyze_button = gr.Button(
        "🔍 Analyze My Finances",
        variant="primary",
    )

    # -------------------------------------------------
    # Financial overview
    # -------------------------------------------------

    gr.Markdown(
        "## 📊 Financial Overview"
    )

    with gr.Row():

        income_output = gr.Textbox(
            label="Income",
            interactive=False,
        )

        expenses_output = gr.Textbox(
            label="Expenses",
            interactive=False,
        )

        savings_output = gr.Textbox(
            label="Savings",
            interactive=False,
        )

        savings_rate_output = gr.Textbox(
            label="Savings Rate",
            interactive=False,
        )

    # -------------------------------------------------
    # Charts
    # -------------------------------------------------

    gr.Markdown(
        "## 📈 Spending Analysis"
    )

    with gr.Row():

        spending_chart = gr.Plot(
            label="Spending by Category"
        )

        trend_chart = gr.Plot(
            label="Spending Trend"
        )

    # -------------------------------------------------
    # Subscriptions
    # -------------------------------------------------

    gr.Markdown(
        "## 🔁 Possible Recurring Subscriptions"
    )

    subscription_output = gr.Dataframe(
        label="Detected Subscriptions",
        interactive=False,
    )

    # -------------------------------------------------
    # Adaptive budget
    # -------------------------------------------------

    gr.Markdown(
        "## 🎯 Adaptive Budget"
    )

    budget_output = gr.Textbox(
        label="Budget Analysis",
        lines=12,
        interactive=False,
    )

    # -------------------------------------------------
    # AI response
    # -------------------------------------------------

    gr.Markdown(
        "## 🤖 FinPilot AI Financial Advisor"
    )

    ai_output = gr.Textbox(
        label="AI Recommendation",
        lines=15,
        interactive=False,
    )

    # -------------------------------------------------
    # Button action
    # -------------------------------------------------

    analyze_button.click(
        fn=analyze_finances,

        inputs=[
            statement_input,
            text_input,
        ],

        outputs=[
            income_output,
            expenses_output,
            savings_output,
            savings_rate_output,
            spending_chart,
            trend_chart,
            subscription_output,
            budget_output,
            ai_output,
        ],
    )


# -------------------------------------------------
# Start application
# -------------------------------------------------

if __name__ == "__main__":

    app.launch()