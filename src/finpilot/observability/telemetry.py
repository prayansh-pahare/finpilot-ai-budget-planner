from agent_framework.observability import configure_otel_providers

def setup_observability():
    """Enable simple FinPilot observability in the terminal."""

    configure_otel_providers(
        env_file_path=".env"
    )
