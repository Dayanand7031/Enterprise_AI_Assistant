from app.services.rag.retrieval_service import retrieve_documents


def print_results(query: str, top_k: int = 5):

    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    results = retrieve_documents(
        query,
        top_k=top_k
    )

    print(f"\nRetrieved documents: {len(results)}")

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result["metadata"]

        print("\n" + "-" * 70)

        print(f"RESULT {index}")
        print(f"Distance: {result['distance']}")

        print(
            f"Content Type: "
            f"{metadata.get('content_type')}"
        )

        print(
            f"Page: "
            f"{metadata.get('page')}"
        )

        print(
            f"Table Type: "
            f"{metadata.get('table_type')}"
        )

        print("\nText:")
        print(result["text"])


print_results(
    "How many privilege leaves are available?"
)


print_results(
    "What is the sandwich leave rule?"
)


print_results(
    "When is Holi?"
)