import json


def parse_mcp_response(result) -> dict:
    """
    Parse and normalize an MCP CallToolResult.

    Returns a consistent dictionary:
    {
        "success": bool,
        ...
    }
    """

    # ---------------------------------------------
    # MCP tool reported an error
    # ---------------------------------------------

    if result.is_error:
        return {
            "success": False,
            "error": "MCP tool execution failed.",
        }

    # ---------------------------------------------
    # MCP returned no content
    # ---------------------------------------------

    if not result.content:
        return {
            "success": False,
            "error": "MCP server returned no content.",
        }

    # ---------------------------------------------
    # Get first content item
    # ---------------------------------------------

    first_content = result.content[0]

    # ---------------------------------------------
    # Validate text response
    # ---------------------------------------------

    if not hasattr(first_content, "text"):
        return {
            "success": False,
            "error": "Unexpected MCP response format.",
        }

    # ---------------------------------------------
    # Parse JSON
    # ---------------------------------------------

    try:
        data = json.loads(
            first_content.text
        )

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Unable to parse MCP tool response.",
        }

    # ---------------------------------------------
    # Validate parsed response
    # ---------------------------------------------

    if not isinstance(data, dict):
        return {
            "success": False,
            "error": "MCP tool returned an invalid response.",
        }

    return data