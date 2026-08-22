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

# =================================================
# BANK STATEMENT DASHBOARD
# =================================================

def analyze_statement_dashboard(statement):
    """Analyze the uploaded bank statement and update the financial dashboard."""

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

    # =============================================
    # Spending Trend
    # =============================================

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

    # =============================================
    # Subscription Detection
    # =============================================

    subscriptions_table = detect_subscriptions(
        statement
    )

    # =============================================
    # Adaptive Budget
    # =============================================

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

    # ---------------------------------------------
    # Add adjustment suggestions
    # ---------------------------------------------

    if budget["adjustment_suggestions"]:

        budget_summary += (
            "\n\nSuggested Adjustments:\n"
        )

        for suggestion in (
            budget["adjustment_suggestions"]
        ):

            budget_summary += (
                f"\n• {suggestion['category']}: "
                f"reduce approximately "
                f"₹{suggestion['suggested_reduction']:,.2f}"
            )

    else:

        budget_summary += (
            "\n\nNo spending reductions are required "
            "to meet the current savings target."
        )

    # ---------------------------------------------
    # Return dashboard values
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
    )


# =================================================
# LEFT SIDE
# AI CHAT
# =================================================

def chat_with_finpilot(
    message,
    history,
    statement,
    agent_session,
):
    """
    Send the user's message to FinPilot and display
    the response in the same conversation window.
    """

    # ---------------------------------------------
    # Ignore empty messages
    # ---------------------------------------------

    if not message or not message.strip():

        return "", history, agent_session

    # ---------------------------------------------
    # Make sure chat history exists
    # ---------------------------------------------

    if history is None:

        history = []

    # ---------------------------------------------
    # Add user's message
    # ---------------------------------------------

    history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    # ---------------------------------------------
    # Ask FinPilot Agent
    # ---------------------------------------------

    try:

        ai_response, agent_session = run_finpilot(
            message,
            statement,
            agent_session,
        )

    except Exception as error:

        ai_response = (
            "Sorry, I could not process your request.\n\n"
            f"Technical details: {error}"
        )

    # ---------------------------------------------
    # Add FinPilot response
    # ---------------------------------------------

    history.append(
        {
            "role": "assistant",
            "content": ai_response,
        }
    )

    # ---------------------------------------------
    # Clear textbox and update conversation
    # ---------------------------------------------

    return "", history, agent_session

# =================================================
# CLEAR CHAT
# =================================================

def clear_chat():
    """Clear the visible chat and start a fresh MAF session."""

    return [], None


# =================================================
# GRADIO USER INTERFACE
# =================================================

with gr.Blocks(
    title="FinPilot AI Budget Planner"
) as app:

    # Stores the Microsoft Agent Framework session for this Gradio user.
    # It allows FinPilot to remember earlier turns in the same conversation.
    agent_session = gr.State(value=None)

    # -------------------------------------------------
    # Main Heading
    # -------------------------------------------------

    gr.Markdown(
        """
        # 💰 FinPilot AI Budget Planner

        ### Agentic AI Personal Finance Assistant

        Chat with FinPilot on the left and analyze your
        bank statement on the right.
        """
    )

    # =================================================
    # MAIN TWO-COLUMN LAYOUT
    # =================================================

    with gr.Row():

        # =============================================
        # LEFT SIDE - CHAT
        # =============================================

        with gr.Column(scale=1):

            gr.Markdown(
                "## 🤖 Chat with FinPilot"
            )

            gr.Markdown(
                """
                Ask questions about budgeting, savings,
                spending, subscriptions or your uploaded
                bank statement.
                """
            )

            chatbot = gr.Chatbot(
                # fn=chat_with_finpilot,
                label="FinPilot Conversation",
                height=300,
            )

            chat_input = gr.Textbox(
                label="Your Message",
                placeholder=(
                    "Example: Analyze my spending and "
                    "tell me how I can save more money."
                ),
                lines=2,
            )

            with gr.Row():

                send_button = gr.Button(
                    "💬 Send",
                    variant="primary",
                )

                clear_button = gr.Button(
                    "🗑️ Clear Chat"
                )

            # -----------------------------------------
            # Subscriptions
            # -----------------------------------------

            gr.Markdown(
                "### 🔁 Recurring Subscriptions"
            )

            subscription_output = gr.Dataframe(
                label="Detected Subscriptions",
                interactive=False,
            )

            # -----------------------------------------
            # Adaptive Budget
            # -----------------------------------------

            gr.Markdown(
                "### 🎯 Adaptive Budget"
            )

            budget_output = gr.Textbox(
                label="Budget Analysis",
                lines=10,
                interactive=False,
            )
            
        # =============================================
        # RIGHT SIDE - FINANCIAL DASHBOARD
        # =============================================

        with gr.Column(scale=1):

            gr.Markdown(
                "## 📊 Financial Dashboard"
            )

            # -----------------------------------------
            # CSV Upload
            # -----------------------------------------

            statement_input = gr.File(
                label="Upload Bank Statement",
                file_types=[".csv"],
                type="filepath",
                height=130,
            )

            analyze_button = gr.Button(
                "🔍 Analyze Statement",
                variant="primary",
            )

            # -----------------------------------------
            # Financial Overview
            # -----------------------------------------

            gr.Markdown(
                "### 💵 Financial Overview"
            )

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

            # -----------------------------------------
            # Spending Pie Chart
            # -----------------------------------------

            gr.Markdown(
                "### 🥧 Spending by Category"
            )

            spending_chart = gr.Plot(
                label="Spending by Category"
            )

            # -----------------------------------------
            # Spending Trend
            # -----------------------------------------

            gr.Markdown(
                "### 📈 Spending Trend"
            )

            trend_chart = gr.Plot(
                label="Daily Spending Trend"
            )

            

    # =================================================
    # EVENTS
    # =================================================

    # -------------------------------------------------
    # Analyze bank statement
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Send chat message using button
    # -------------------------------------------------

    send_button.click(
        fn=chat_with_finpilot,

        inputs=[
            chat_input,
            chatbot,
            statement_input,
            agent_session,
        ],

        outputs=[
            chat_input,
            chatbot,
            agent_session,
        ],
    )

    # -------------------------------------------------
    # Press Enter to send chat message
    # -------------------------------------------------

    chat_input.submit(
        fn=chat_with_finpilot,

        inputs=[
            chat_input,
            chatbot,
            statement_input,
            agent_session,
        ],

        outputs=[
            chat_input,
            chatbot,
            agent_session,
        ],
    )

    # -------------------------------------------------
    # Clear Chat
    # -------------------------------------------------

    clear_button.click(
        fn=clear_chat,
        inputs=[],
        outputs=[
            chatbot,
            agent_session,
        ],
    )


# =================================================
# START APPLICATION
# =================================================

if __name__ == "__main__":

    app.launch()