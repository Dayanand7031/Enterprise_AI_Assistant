def get_capabilities_response() -> str:
    return """I can currently help you with:

1. Company Policy & Document RAG
   Ask questions about company policies and uploaded company documents.

2. Local Ticket Management through MCP
   Create, read, update, and delete tickets using the local PostgreSQL-backed ticket system.

3. Jira Cloud through MCP
   Create, read, update, and list Jira Cloud issues through the connected Jira integration, subject to your permissions.

Examples:

• "What is the company leave policy?"
• "Create a ticket for a login API failure"
• "Show me Jira tickets in project KAN"
• "Get Jira issue KAN-5"
• "Update Jira issue KAN-5"
"""