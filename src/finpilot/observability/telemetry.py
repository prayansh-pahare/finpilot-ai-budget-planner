from agent_framework.observability import configure_otel_providers, enable_instrumentation
from langfuse import get_client


def setup_observability():
    # """Enable simple FinPilot observability in the terminal."""
    
    # configure_otel_providers(
    #     env_file_path=".env"
    # )
    
    """Enable FinPilot telemetry with Langfuse."""

    langfuse = get_client()

    if langfuse.auth_check():
        print("Langfuse connected successfully")
    else:
        print("Langfuse authentication failed")

    enable_instrumentation(
        enable_sensitive_data=False
    )

    return langfuse