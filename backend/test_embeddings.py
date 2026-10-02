from app.services.rag.embedding_service import (
    generate_embedding,
    generate_embeddings,
)


print("=" * 70)
print("EMBEDDING TEST")
print("=" * 70)


text = "Privilege Leave entitlement is 24 days per annum."


embedding = generate_embedding(text)


print("\nSingle embedding:")
print("Vector type:", type(embedding))
print("Vector dimensions:", len(embedding))
print("First 10 values:")
print(embedding[:10])


texts = [
    "Privilege Leave entitlement is 24 days per annum.",
    "Employees are entitled to 7 days of Sick Leave.",
    "Holi is a holiday on 22-Mar.",
]


embeddings = generate_embeddings(texts)


print("\nMultiple embeddings:")
print("Number of texts:", len(embeddings))
print("Dimensions:", len(embeddings[0]))


print("\nEmbedding test completed.")