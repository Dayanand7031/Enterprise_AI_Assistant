from app.services.rag.rag_service import (
    generate_rag_response,
)


def test_query(query: str):

    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    result = generate_rag_response(
        query,
        top_k=5
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"{index}. "
            f"{source['filename']} | "
            f"Page {source['page']} | "
            f"{source['content_type']} | "
            f"Distance: {source['distance']}"
        )


test_query(
    "How many privilege leaves are available?"
)


test_query(
    "What is the sandwich leave rule?"
)


test_query(
    "When is Holi?"
)


test_query(
    "What is the company's work from home policy?"
)