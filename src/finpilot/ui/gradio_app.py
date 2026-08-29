import os
import gradio as gr
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path

# Dir of FinPilot services & agents
FINPILOT_DIR = Path(__file__).resolve().parent.parent
SERVICES_DIR = FINPILOT_DIR / "services"
AGENTS_DIR = FINPILOT_DIR / "agents"

sys.path.append(str(SERVICES_DIR))
sys.path.append(str(AGENTS_DIR))

# Import FinPilot features
from statement_parser import load_and_categorize_statement
from subscription_detector import detect_subscriptions
from spending_patterns import calculate_daily_spending
from adaptive_budget import create_adaptive_budget
from finance_agent import run_finpilot

# Store current statement and MAF session
current_statement = None
finpilot_session = None

# =================================================
# BANK STATEMENT DASHBOARD
# =================================================

def analyze_statement_dashboard(statement):
    """Analyze the uploaded bank statement and update the financial dashboard."""

    global current_statement

    # No file uploaded
    if statement is None:
        return (
            "₹0",
            "₹0",
            "₹0",
            "0%",
            None,
            None,
            pd.DataFrame(),
            "Please upload a bank statement.",
        )

    current_statement = statement

    # Try reading the statement
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
            (
                "FinPilot could not read this bank statement.\n\n"
                "Please upload a valid CSV file containing:\n\n"
                "date, description, amount, type\n\n"
                f"Technical details: {error}"
            ),
        )

    # Total Income
    income = df[
        df["type"].str.upper() == "CREDIT"
    ]["amount"].sum()

    # Total Expenses
    expenses = df[
        df["type"].str.upper() == "DEBIT"
    ]["amount"].sum()

    # Total Savings
    savings = income - expenses

    # Savings Rate
    if income > 0:
        savings_rate = (savings / income) * 100
    else:
        savings_rate = 0
        
    # Convert numbers to display text
    income_text = f"₹{income:,.2f}"
    expenses_text = f"₹{expenses:,.2f}"
    savings_text = f"₹{savings:,.2f}"
    savings_rate_text = (f"{savings_rate:.2f}%")


    # Spending By Category
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

    # Spending Trend
    daily_spending = calculate_daily_spending(statement)

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

    # Subscription Detection
    subscriptions_table = detect_subscriptions(statement)

    # Adaptive Budget
    budget = create_adaptive_budget(statement)

    budget_summary = (
        f"Months analyzed: {budget['months_analyzed']}\n\n"
        f"Average monthly income: ₹{budget['average_monthly_income']:,.2f}\n"
        f"Average monthly expenses: ₹{budget['average_monthly_expenses']:,.2f}\n"
        f"Average monthly savings: ₹{budget['average_monthly_savings']:,.2f}\n\n"
        f"Savings target: ₹{budget['savings_target']:,.2f}\n"
        f"On track: {budget['on_track']}"
    )

    # Add adjustment suggestions
    if budget["adjustment_suggestions"]:
        budget_summary += ("\n\nSuggested Adjustments:\n")

        for suggestion in (budget["adjustment_suggestions"]):
            budget_summary += (
                f"\n• {suggestion['category']}: reduce approximately ₹{suggestion['suggested_reduction']:,.2f}"
            )
    else:
        budget_summary += (
            "\n\nNo spending reductions are required to meet the current savings target."
        )
        
    # Return dashboard values
    return (
        income_text,
        expenses_text,
        savings_text,
        savings_rate_text,
        spending_chart,
        trend_chart,
        subscriptions_table,
        budget_summary,
    )


# =================================================
# AI CHAT FUNCTION
# =================================================

def chat_with_finpilot(message, history):
    """Send the user's message to FinPilot and display the response in the same conversation window."""

    global finpilot_session
    global current_statement

    # Ignore empty messages
    if not message or not message.strip():
        return ""

    # Ask FinPilot Agent
    try:
        ai_response, finpilot_session = run_finpilot(
            message,
            current_statement,
            finpilot_session,
        )
        return ai_response
    
    except Exception as error:
        return (
            "Sorry, I could not process your request.\n\n"
            f"Technical details: {error}"
        )

# =================================================
# GRADIO USER INTERFACE
# =================================================

with gr.Blocks(title="FinPilot AI Budget Planner") as app:
    # Main Heading
    gr.Markdown("""# FinPilot - Agentic AI Personal Finance Assistant""")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""Ask questions or your uploaded bank statement.""")

            gr.ChatInterface(
                fn=chat_with_finpilot,
                # chatbot=gr.Chatbot(
                #     label="FinPilot Conversation",
                #     height=300,
                # ),
            )
            
            # Subscriptions
            gr.Markdown("### Recurring Subscriptions")

            subscription_output = gr.Dataframe(
                label="Detected Subscriptions",
                interactive=False,
            )

            # Adaptive Budget
            gr.Markdown("### Adaptive Budget")

            budget_output = gr.Textbox(
                label="Budget Analysis",
                lines=10,
                interactive=False,
            )
            
        # FINANCIAL DASHBOARD
        with gr.Column(scale=1):
            gr.Markdown("## Financial Dashboard")

            # CSV Upload
            statement_input = gr.File(
                label="Upload Bank Statement",
                file_types=[".csv"],
                type="filepath",
                height=130,
            )

            analyze_button = gr.Button(
                "Analyze Statement",
                variant="primary",
            )

            # Financial Overview
            gr.Markdown("### Financial Overview")

            with gr.Row():
                income_output = gr.Textbox(
                    label="Total Income",
                    value="₹0",
                    interactive=False,
                )
                expenses_output = gr.Textbox(
                    label="Total Expense",
                    value="₹0",
                    interactive=False,
                )
            with gr.Row():
                savings_output = gr.Textbox(
                    label="Total Saving",
                    value="₹0",
                    interactive=False,
                )
                savings_rate_output = gr.Textbox(
                    label="Saving Rate",
                    value="0%",
                    interactive=False,
                )

            # Spending Pie Chart
            gr.Markdown("### Spending by Category")

            spending_chart = gr.Plot(
                label="Spending by Category"
            )

            # Spending Trend
            gr.Markdown("### Spending Trend")

            trend_chart = gr.Plot(
                label="Daily Spending Trend"
            )

    # =================================================
    # CLICK EVENTS - Analyze bank statement
    # =================================================
    analyze_button.click(
        fn=analyze_statement_dashboard,
        inputs=[
            statement_input,
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
        ],
    )

# =================================================
# START APPLICATION
# =================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
    )