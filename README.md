# FinPilot - Agentic AI Personal Finance Assistant

FinPilot is a **single-agent Agentic AI personal finance assistant** that turns CSV bank statements into understandable financial insights. It combines deterministic Python/Pandas analysis with an AI finance agent built using the **Microsoft Agent Framework (MAF)**, **Ollama**, and **Model Context Protocol (MCP)**.

Users can upload a bank statement to view income, expenses, savings, spending categories, recurring subscriptions, spending trends, and an adaptive budget. They can also chat with FinPilot in natural language and ask questions about their finances or the currently uploaded statement.

**Live Demo:** https://finpilot-ai-budget-planner.onrender.com  
**Repository:** https://github.com/prayansh-pahare/finpilot-agentic-ai-personal-finance-assistant

> **Disclaimer:** FinPilot is an educational project and does not provide professional financial advice.


## Project Goal

Understanding a bank statement manually can be time-consuming. FinPilot is designed to make that process easier by combining reliable financial calculations with conversational AI.

The project separates responsibilities deliberately:

- **Python/Pandas** performs calculations and statement analysis.
- **The AI agent** understands the user's intent and explains results.
- **MCP** exposes financial capabilities to the agent as tools.
- **Gradio** provides the web interface.
- **OpenTelemetry + Langfuse** provide observability for agent/model execution.

This reduces the chance of the language model inventing financial totals while still allowing the user to interact with the system naturally.

The system can accept both:

- Bank statement files (currently CSV supported with this release)
- Free-text financial questions and information.

It combines AI reasoning with reliable Python financial calculations.

## Main Features

- CSV bank-statement upload and validation
- Income, expense, savings, and savings-rate calculation
- Rule-based transaction categorization
- Spending-by-category visualization
- Daily spending-trend visualization
- Detection of possible recurring subscriptions
- Basic 50/30/20 budget generation
- Adaptive monthly budget based on historical spending
- Suggested spending reductions when savings are below target
- Budget versioning and comparison using local JSON history
- Conversational financial assistant using Microsoft Agent Framework
- MCP-based financial tool calling
- Reusable MAF session for follow-up conversation memory
- Ollama-hosted LLM integration
- OpenTelemetry/Langfuse tracing and token-usage observability
- Gradio dashboard and chat interface
- Render deployment support


## Architecture

```text
                         User
                          |
                          v
                    Gradio Web UI
                   /             \
                  /               \
     Financial Dashboard        AI Chat
             |                      |
             v                      v
       Python / Pandas       FinPilot Finance Agent
       Service Layer          Microsoft Agent Framework
             |                      |
             |                      v
             |                 Ollama LLM
             |                      |
             |               decides whether a
             |                tool is required
             |                      |
             |                      v
             +-------------- MCP stdio server
                                    |
                                    v
                           Financial MCP Tools
                                    |
                                    v
                           Python Service Layer

           Agent / model telemetry ---> OpenTelemetry ---> Langfuse
```

FinPilot uses a **single agent with multiple tools**. The agent is responsible for reasoning and tool selection; the individual financial calculations remain normal Python functions.

## Agentic AI Flow

For a question such as:

> "Analyze my statement and tell me how I can improve my savings."

FinPilot follows this general flow:

1. Gradio sends the user's message to the Finance Agent.
2. The agent interprets the request and conversation context.
3. The model decides whether exact financial data is required.
4. When necessary, the agent invokes an MCP financial tool.
5. The MCP server calls the appropriate Python/Pandas service.
6. The calculated result is returned to the agent.
7. The agent explains the result in simple language.
8. The same MAF session can be reused for follow-up questions.

This means the LLM does not need to guess statement totals or perform all calculations itself.


## MCP Financial Tools

The MCP server provides the Finance Agent with a small set of purpose-built tools:

| Tool | Purpose |
| --- | --- |
| `calculate_savings` | Calculate savings and savings rate from income and expenses. |
| `analyze_statement` | Return statement totals and category spending. |
| `detect_subscriptions` | Find possible recurring subscriptions. |
| `create_budget` | Generate a basic 50/30/20 budget. |
| `create_adaptive_budget` | Generate an adaptive monthly budget from statement history. |
| `adjust_budget` | Compare a new adaptive budget with the previous saved budget. |

The agent can select these tools when a question requires reliable calculations or bank-statement analysis.


## Expected CSV Format

Current FinPilot expects a CSV bank statement containing these columns:

```csv
date,description,amount,type
2026-01-01,SALARY CREDIT,60000,CREDIT
2026-01-03,RENT,15000,DEBIT
2026-01-05,SWIGGY,650,DEBIT
2026-01-08,NETFLIX,649,DEBIT
```

Invalid or incomplete statements are handled by the UI and will produce a readable validation message rather than stopping the entire application.


## Adaptive Budgeting

The adaptive budget service analyzes historical transactions across the months present in the statement. It calculates:

- Average monthly income
- Average monthly expenses
- Average monthly savings
- 50% needs target
- 30% wants target
- 20% savings target
- Savings gap
- Average spending by category
- Whether the user is currently on track

When actual savings are below the target, FinPilot can recommend reductions in adjustable categories such as food, shopping, entertainment, transport, and health/fitness.

FinPilot maintain simple budget history using JSON storage. `budget_history.py` adds a simple continuous-adjustment mechanism by saving the latest budget and comparing it with the previous saved version.


## Observability with Langfuse

FinPilot uses its Agent Framework/OpenTelemetry instrumentation with **Langfuse** to inspect agent execution.

Depending on the emitted trace, Langfuse can show:

- Agent invocations
- LLM generations
- MCP/tool calls
- Execution latency
- Input/prompt tokens
- Output/completion tokens
- Total token usage
- Trace hierarchy

It shows the agent making an LLM call, invoke an MCP tool, observe its result, and then make another LLM call to create the final response.

### Langfuse Sample Trace

A sample FinPilot agent execution can be viewed here:

[View FinPilot Langfuse Sample Trace 1](https://us.cloud.langfuse.com/project/cmt3wctb608baad0deev3axbc/traces/a6be3f2b36027fca5e36ac7aeaf50289)

[View FinPilot Langfuse Sample Trace 2](https://us.cloud.langfuse.com/project/cmt3wctb608baad0deev3axbc/traces/f97b4099e1a8b2979d9483b30806bacf)

> The public trace uses synthetic financial data and does not contain real banking information.

## Project Structure

```text
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
│       │   ├── finance_agent.py
│       │   └── first_agent_test.py
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
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/prayansh-pahare/finpilot-ai-budget-planner.git
cd finpilot-ai-budget-planner
```

### 2. Install dependencies with uv

The project uses Python 3.12+ and `uv` for dependency management.

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root. Use your own credentials:

```env
OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_HOST=https://ollama.com
OLLAMA_MODEL=your_model_name

LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

## Run Locally

Start the complete Gradio application:

```bash
uv run python src/finpilot/ui/gradio_app.py
```


## Deployment on Render

The application is deployed as a Render Web Service.
- https://finpilot-ai-budget-planner.onrender.com

Typical configuration:

```text
Build Command: uv sync
Start Command: uv run python src/finpilot/ui/gradio_app.py
```

The Ollama and Langfuse environment variables are added in the Render service settings. And the Gradio application will listen on `0.0.0.0` and use Render's `PORT` environment variable.

> Note: Render free instances can spin down after inactivity, so the first request after an idle period may take longer.

## Future Enhancements

Possible future improvements include:

- PDF and Excel bank-statement support
- Automatic bank-statement column mapping
- More advanced transaction categorization
- Database-backed user profiles
- Long-term persistent financial memory
- Goal-based savings planning
- Spending anomaly detection
- Multiple user support
- Cloud deployment
- Authentication
- Improved financial visualizations
- Additional MCP tools
- Multi-agent architecture for larger financial workflows


## Tech Stack

- **Python 3.12+**
- **Microsoft Agent Framework**
- **Ollama / Ollama Cloud**
- **Model Context Protocol (MCP)**
- **Pandas**
- **Plotly**
- **Gradio**
- **OpenTelemetry**
- **Langfuse**
- **uv**
- **Render**


## Author

**Prayansh Pahare**

Built as an Agentic AI capstone project demonstrating how an LLM agent can reason about a user's request, select standardized MCP tools, use deterministic financial services, preserve conversational context, and expose the process through an observable web application.
