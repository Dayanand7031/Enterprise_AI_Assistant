from app.services.planner_service import plan_query


queries = [
    "How many privilege leaves are available?",
    "Is Holi a company holiday?",
    "Create a Jira ticket for the login bug.",
    "Check the status of Jira ticket PROJ-123.",
    "Compare LangGraph and CrewAI for enterprise agent orchestration.",
    "Research the best architecture for an enterprise AI assistant.",
]


for query in queries:
    result = plan_query(query)

    print("\n==============================")
    print("Query:")
    print(query)

    print("Route:")
    print(result["route"])

    print("Reason:")
    print(result["reason"])