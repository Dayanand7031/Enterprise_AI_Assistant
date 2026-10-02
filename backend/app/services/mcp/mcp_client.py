import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def create_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp.server",
        ],
        cwd=str(PROJECT_ROOT),
    )


async def discover_tools():
    server_params = create_server_params()

    async with Client(server_params) as client:
        result = await client.list_tools()
        return result.tools


async def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    created_by: int | None = None,
):
    server_params = create_server_params()

    async with Client(server_params) as client:
        result = await client.call_tool(
            "create_ticket",
            {
                "title": title,
                "description": description,
                "priority": priority,
                "created_by": created_by,
            },
        )

        return result

async def get_ticket(ticket_id: int):
    server_params = create_server_params()

    async with Client(server_params) as client:

        result = await client.call_tool(
            "get_ticket",
            {
                "ticket_id": ticket_id,
            },
        )

        return result

async def list_tickets():
    server_params = create_server_params()

    async with Client(server_params) as client:

        result = await client.call_tool(
            "list_tickets",
            {},
        )

        return result

async def update_ticket(
    ticket_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    status: str | None = None,
):
    server_params = create_server_params()

    async with Client(server_params) as client:

        arguments = {
            "ticket_id": ticket_id,
        }

        if title is not None:
            arguments["title"] = title

        if description is not None:
            arguments["description"] = description

        if priority is not None:
            arguments["priority"] = priority

        if status is not None:
            arguments["status"] = status

        result = await client.call_tool(
            "update_ticket",
            arguments,
        )

        return result


async def main():
    print("\n========== MCP CLIENT TEST ==========")

    # -----------------------------------
    # 1. Discover tools
    # -----------------------------------

    print("\nConnecting to MCP server...")

    tools = await discover_tools()

    print("\nDiscovered tools:")

    for tool in tools:
        print(f"- {tool.name}")

    # -----------------------------------
    # 2. Invoke create_ticket
    # -----------------------------------

    print("\nInvoking create_ticket...")

    result = await create_ticket(
        title="Login page not working",
        description="Users receive a 500 error when attempting to log in.",
        priority="high",
    )

    print("\nTool result:")
    print(result)

    print("\nStructured content:")
    print(result.structured_content)

    print("\nIs error:")
    print(result.is_error)


if __name__ == "__main__":
    asyncio.run(main())