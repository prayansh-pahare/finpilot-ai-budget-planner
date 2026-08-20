import gradio as gr
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path

FINPILOT_DIR = Path(__file__).resolve().parent.parent

SERVICES_DIR = FINPILOT_DIR / "services"
AGENTS_DIR = FINPILOT_DIR / "agents"

sys.path.append(str(SERVICES_DIR))
sys.path.append(str(AGENTS_DIR))

from statement_parser import load_and_categorize_statement
from finance_agent import run_finpilot


def analyze_finances(statement, user_message):
    """Analyze a bank statement and answer financial questions."""

    if statement is None and not user_message:
        return (
            "Please upload a bank statement or enter a message.",
            None,
        )

    summary = ""
    chart = None

    # -----------------------------------
    # 1. Analyze uploaded bank statement
    # -----------------------------------

    if statement is not None:

        df = load_and_categorize_statement(statement)

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

        summary += (
            "BANK STATEMENT SUMMARY\n\n"
            f"Monthly Income: ₹{income:,.2f}\n"
            f"Total Expenses: ₹{expenses:,.2f}\n"
            f"Current Savings: ₹{savings:,.2f}\n"
            f"Savings Rate: {savings_rate:.2f}%\n"
        )

        expenses_df = df[
            df["type"].str.upper() == "DEBIT"
        ]

        category_totals = (
            expenses_df
            .groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        chart = px.pie(
            category_totals,
            names="category",
            values="amount",
            title="Spending by Category",
        )

    # -----------------------------------
    # 2. Send free text to FinPilot Agent
    # -----------------------------------

    if user_message:
        ai_answer = run_finpilot(
            user_message,
            statement,
        )

        summary += (
            "\n\nFINPILOT AI RESPONSE\n\n"
            f"{ai_answer}"
        )

    return summary, chart

with gr.Blocks(title="FinPilot AI Budget Planner") as app:

    gr.Markdown(
        """
        # 💰 FinPilot AI Budget Planner

        Upload your bank statement or describe your financial situation.
        """
    )

    statement_input = gr.File(
        label="Upload Bank Statement",
        file_types=[".csv"],
        type="filepath",
    )

    text_input = gr.Textbox(
        label="Tell FinPilot About Your Finances",
        placeholder=(
            "Example: I earn ₹60,000 per month and want "
            "to save ₹15,000."
        ),
        lines=4,
    )

    analyze_button = gr.Button(
        "Analyze My Finances"
    )

    output = gr.Textbox(
        label="Financial Summary",
        lines=10,
    )

    spending_chart = gr.Plot(
        label="Spending by Category"
    )

    analyze_button.click(
        fn=analyze_finances,
        inputs=[
            statement_input,
            text_input,
        ],
        outputs=[
            output,
            spending_chart,
        ],
    )


if __name__ == "__main__":
    app.launch()