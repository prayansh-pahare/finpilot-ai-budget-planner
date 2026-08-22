import asyncio
import os

from dotenv import load_dotenv
from ollama import AsyncClient

from agent_framework import Agent
from agent_framework.ollama import OllamaChatClient
from agent_framework import MCPStdioTool

import sys
from pathlib import Path

OBSERVABILITY_DIR = (Path(__file__).resolve().parent.parent / "observability")

sys.path.append(str(OBSERVABILITY_DIR))

from telemetry import setup_observability

setup_observability()
load_dotenv()


async def ask_finpilot(
    user_message: str,
    statement_path: str | None = None,
    session=None,
):
    """Ask the FinPilot AI agent a financial question using a reusable MAF session."""

    api_key = os.getenv("OLLAMA_API_KEY")
    host = os.getenv("OLLAMA_HOST")
    model = os.getenv("OLLAMA_MODEL")

    ollama_client = AsyncClient(
        host=host,
        headers={
            "Authorization": f"Bearer {api_key}"
        },
    )

    chat_client = OllamaChatClient(
        model=model,
        client=ollama_client,
    )

    mcp_tool = MCPStdioTool(
        name="FinPilot Financial Tools",
        command="uv",
        args=[
            "run",
            "python",
            "src/finpilot/mcp/server.py",
        ],
    )

    async with mcp_tool:

        agent = Agent(
            client=chat_client,
            name="FinPilotFinancialAnalyst",
            instructions=(
                "You are FinPilot, a helpful personal finance assistant. "
                "Use the available MCP financial tools whenever calculations "
                "or bank statement analysis are required. "
                "Do not invent financial numbers. "
                "Explain financial information in simple language. "
                "Treat detected subscriptions as possible subscriptions, "
                "not automatically unnecessary expenses."
            ),
            tools=[mcp_tool],
        )

        # Create a new Microsoft Agent Framework session only for
        # the first message. The same session is reused for later turns.
        if session is None:
            session = agent.create_session()

        if statement_path:
            final_prompt = f"""
The user currently has a bank statement uploaded at:

{statement_path}

Use the available MCP tools to analyze this statement when needed.
Do not analyze the file unless it is relevant to the user's request.

User's request:

{user_message}
"""
        else:
            final_prompt = user_message

        result = await agent.run(
            final_prompt,
            session=session,
        )

        return str(result), session


def run_finpilot(
    user_message: str,
    statement_path: str | None = None,
    session=None,
):
    """Run FinPilot and return both the answer and reusable MAF session."""

    return asyncio.run(
        ask_finpilot(
            user_message,
            statement_path,
            session,
        )
    )


if __name__ == "__main__":

    answer, session = run_finpilot(
        "I earn 60000 rupees per month and spend "
        "45000 rupees. How much am I saving?"
    )

    print(answer)
