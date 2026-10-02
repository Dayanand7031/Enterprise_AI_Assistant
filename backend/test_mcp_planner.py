from app.services.mcp.mcp_planner_service import plan_mcp_action


test_cases = [
    "Get Jira issue KAN-5",

    "Update Jira issue KAN-5 and change the title to Login API failure",

    "Create a Jira ticket in project KAN for login API returning 500 errors",

    "Find all Jira tickets in project KAN",

    "Create a ticket for the employee login problem",
]


for i, query in enumerate(test_cases, start=1):

    print("\n" + "=" * 70)
    print(f"TEST {i}")
    print("QUERY:", query)
    print("=" * 70)

    result = plan_mcp_action(
        query=query,
        history=[]
    )

    print("RESULT:")
    print(result)