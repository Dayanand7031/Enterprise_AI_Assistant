from langgraph.graph import StateGraph, START, END

from app.graph.state import ChatState

from app.graph.nodes import (
    planner,
    route_after_planner,

    # General conversation nodes
    greeting_node,
    capabilities_node,

    # RAG
    prepare_query,
    retrieve,
    evaluate_retrieval_node,
    route_after_evaluation,
    retry_query,
    generate,
    fallback,

    # MCP / CrewAI
    mcp_node,
    crewai_placeholder,
)


def build_chat_graph():

    graph = StateGraph(ChatState)

    # -------------------------
    # Planner
    # -------------------------

    graph.add_node(
        "planner",
        planner
    )

    # -------------------------
    # General conversation nodes
    # -------------------------

    graph.add_node(
        "greeting",
        greeting_node
    )

    graph.add_node(
        "capabilities",
        capabilities_node
    )

    # -------------------------
    # RAG nodes
    # -------------------------

    graph.add_node(
        "prepare_query",
        prepare_query
    )

    graph.add_node(
        "retrieve",
        retrieve
    )

    graph.add_node(
        "evaluate_retrieval",
        evaluate_retrieval_node
    )

    graph.add_node(
        "retry_query",
        retry_query
    )

    graph.add_node(
        "generate",
        generate
    )

    graph.add_node(
        "fallback",
        fallback
    )

    # -------------------------
    # MCP / CrewAI placeholders
    # -------------------------

    graph.add_node(
        "mcp",
        mcp_node
    )

    graph.add_node(
        "crewai",
        crewai_placeholder
    )

    # -------------------------
    # START → Planner
    # -------------------------

    graph.add_edge(
        START,
        "planner"
    )

    # -------------------------
    # Planner routing
    # -------------------------

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "greeting": "greeting",
            "capabilities": "capabilities",
            "rag": "prepare_query",
            "mcp": "mcp",
            "crewai": "crewai",
        }
    )

    # -------------------------
    # RAG workflow
    # -------------------------

    graph.add_edge(
        "prepare_query",
        "retrieve"
    )

    graph.add_edge(
        "retrieve",
        "evaluate_retrieval"
    )

    graph.add_conditional_edges(
        "evaluate_retrieval",
        route_after_evaluation,
        {
            "generate": "generate",
            "retry": "retry_query",
            "fallback": "fallback",
        }
    )

    graph.add_edge(
        "retry_query",
        "retrieve"
    )

    # -------------------------
    # END
    # -------------------------

    graph.add_edge(
        "generate",
        END
    )

    graph.add_edge(
        "fallback",
        END
    )

    graph.add_edge(
        "greeting",
        END
    )

    graph.add_edge(
        "capabilities",
        END
    )


    graph.add_edge(
        "mcp",
        END
    )

    graph.add_edge(
        "crewai",
        END
    )

    return graph.compile()


chat_graph = build_chat_graph()