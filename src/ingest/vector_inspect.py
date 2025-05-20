from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

results, _ = client.scroll(
    collection_name="docs",
    limit=10,
    with_payload=True,
    with_vectors=True 
)

for point in results:
    print(f"🆔 ID: {point.id}")
    print(f"📄 File: {point.payload.get('source_file')}")
    print(f"🧠 Text: {point.payload.get('text')[:100]}...")
    print(f"🔢 Vector (first 5 dims): {point.vector[:5]}...\n")