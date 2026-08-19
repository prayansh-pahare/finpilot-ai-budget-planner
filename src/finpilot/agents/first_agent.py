import asyncio
import os

from dotenv import load_dotenv
from ollama import AsyncClient

from agent_framework import Agent
from agent_framework.ollama import OllamaChatClient


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

    agent = Agent(
        client=chat_client,
        name="FinPilotAssistant",
        instructions=(
            "You are FinPilot, a helpful personal budgeting assistant. "
            "Explain financial concepts in simple language."
        ),
    )

    result = await agent.run(
        "What is a personal budget? Explain it in 3 simple sentences."
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())