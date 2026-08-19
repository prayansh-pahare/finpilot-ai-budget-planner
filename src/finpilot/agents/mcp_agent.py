import asyncio
import os

from dotenv import load_dotenv
from ollama import AsyncClient

from agent_framework import Agent
from agent_framework.ollama import OllamaChatClient
from agent_framework import MCPStdioTool


load_dotenv()


async def main():
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
                "You are FinPilot, a personal finance analysis agent. "
                "Use the available MCP financial tools whenever financial "
                "calculations or bank statement analysis are required. "
                "Do not invent transaction totals or financial numbers. "
                "Explain results in simple language. "
                "Treat detected subscriptions as possible subscriptions, "
                "not automatically unnecessary expenses."
            ),
            tools=[mcp_tool],
        )

        result = await agent.run(
            """
Analyze the bank statement located at:

data/sample_statement.csv

Please:
1. Analyze income and expenses.
2. Calculate savings and savings rate.
3. Identify possible subscriptions.
4. Create a suggested starting budget.
5. Give me a short financial summary.
"""
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())