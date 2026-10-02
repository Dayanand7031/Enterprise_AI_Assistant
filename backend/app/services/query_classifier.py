GREETING_WORDS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "good morning",
    "good afternoon",
    "good evening",
}


def is_greeting(query: str) -> bool:
    normalized = query.strip().lower()

    return normalized in GREETING_WORDS


def get_greeting_response() -> str:
    return (
        "Hello! 👋 I'm the Enterprise AI Assistant. "
        "I can help with company policies, local tickets "
        "through MCP, and Jira Cloud operations."
    )