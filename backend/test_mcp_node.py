import asyncio

from app.graph.nodes import mcp_node


async def main():

    test_cases = [
        {
            "query": "Get Jira issue KAN-5",
            "user_id": 4,
        },
        {
            "query": "Find all Jira tickets in project KAN",
            "user_id": 4,
        },
        {
            "query": "Update Jira issue KAN-5 and change the title to Login API failure",
            "user_id": 4,
        },
        {
            "query": "Create a Jira ticket in project KAN for testing the MCP integration",
            "user_id": 4,
        },
    ]

    for index, test in enumerate(test_cases, start=1):

        print("\n" + "=" * 70)
        print(f"TEST {index}")
        print("QUERY:", test["query"])
        print("=" * 70)

        state = {
            "query": test["query"],
            "history": [],
            "user_id": test["user_id"],
        }

        try:
            result = await mcp_node(state)

            print("\nRESULT:")
            print(result)

        except Exception as e:
            print("\nERROR:")
            print(type(e).__name__, str(e))


if __name__ == "__main__":
    asyncio.run(main())