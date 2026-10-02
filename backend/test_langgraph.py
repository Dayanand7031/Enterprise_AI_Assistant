import asyncio

from app.graph.workflow import chat_graph


async def main():

    queries = [
        "How many privilege leaves are available?",
        "Create a Jira ticket for the login bug.",
        "Research the best architecture for an enterprise AI assistant.",
    ]

    for query in queries:

        result = await chat_graph.ainvoke({
            "query": query,
            "history": []
        })

        print("\n========================================")
        print("QUERY:")
        print(query)

        print("\nPLANNER ROUTE:")
        print(result.get("planner_route"))

        print("\nPLANNER REASON:")
        print(result.get("planner_reason"))

        print("\nANSWER:")
        print(result.get("answer"))

        print("\nSOURCES:")
        print(result.get("sources"))


if __name__ == "__main__":
    asyncio.run(main())