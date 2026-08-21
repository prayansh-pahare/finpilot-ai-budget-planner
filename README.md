# FinPilot AI Budget Planner

FinPilot is an Agentic AI personal finance assistant that analyzes bank statements, detects spending patterns and recurring subscriptions, creates adaptive budgets, and provides personalized financial recommendations.

## Project Objective

The goal of FinPilot is to help users understand their financial behavior and improve their budgeting decisions using Agentic AI.

The system can accept both:
- Bank statement files
- Free-text financial questions

It combines AI reasoning with reliable Python financial calculations.

## Main Features
- Upload and analyze bank statements
- Free-text financial input
- Automatic transaction categorization
- Spending-by-category analysis
- Spending trend visualization
- Recurring subscription detection
- Savings and savings-rate calculation
- Personalized budget generation
- Adaptive monthly budgeting
- Continuous budget adjustment using previous budget history
-  AI-generated financial recommendations
- MCP-based financial tools
- OpenTelemetry observability
- Gradio web dashboard

## Folder Structure
```
finpilot-ai-budget-planner/
│
├── data/
│   ├── sample_statement.csv
│   └── budget_history.json
│
├── src/
│   └── finpilot/
│       │
│       ├── agents/
│       │   ├── first_agent.py
│       │   ├── mcp_agent.py
│       │   └── finance_agent.py
│       │
│       ├── mcp/
│       │   └── server.py
│       │
│       ├── services/
│       │   ├── categorizer.py
│       │   ├── statement_parser.py
│       │   ├── spending_analysis.py
│       │   ├── spending_patterns.py
│       │   ├── subscription_detector.py
│       │   ├── budget_planner.py
│       │   ├── adaptive_budget.py
│       │   └── budget_history.py
│       │
│       ├── observability/
│       │   └── telemetry.py
│       │
│       └── ui/
│           └── gradio_app.py
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```
## Setup
1. Clone the repository
2. Install UV
3. Install project dependencies
    ```
    uv sync
    ```
4. Configure environment variables

    Create a .env file:
    ```text
    OLLAMA_API_KEY=your_api_key
    OLLAMA_HOST=https://ollama.com
    OLLAMA_MODEL=gpt-oss:120b

    ENABLE_CONSOLE_EXPORTERS=true
    ```
    Never commit the .env file.

## Run FinPilot

Start the Gradio application:
```
uv run python src/finpilot/ui/gradio_app.py
```
Then open the Gradio URL provided by GitHub Codespaces.

