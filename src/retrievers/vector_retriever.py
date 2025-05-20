from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

# --- Connect to Qdrant ---
client = QdrantClient("localhost", port=6333)

# --- Load the same model used for uploading embeddings ---
model = SentenceTransformer("all-MiniLM-L6-v2")


def query_vector_db(query, domain=None, confidence_threshold=0.0, source_types=['pdf','email']):
    vector = model.encode(query).tolist()

    must_conditions = []
    if domain:
        must_conditions.append(
            FieldCondition(
                key="domain",
                match=MatchValue(value=domain)
            )
        )
    if source_types:
        must_conditions.append(
            FieldCondition(
                key="source_type",
                match=MatchAny(any=source_types)
            )
        )
    search_filter = Filter(must=must_conditions) if must_conditions else None

    hits = client.search(
        collection_name="docs",
        query_vector=vector,
        limit=3,  # fetch more to apply filtering
        query_filter=search_filter
    )

    # ✅ Filter based on confidence score
    return [hit.payload["text"] for hit in hits if hit.score >= confidence_threshold]
    # return [{"text": hit.payload["text"], "file": hit.payload.get("source_file", "unknown")} for hit in hits]


# --- Test the retriever ---
if __name__ == "__main__":
    results = query_vector_db(
        "what lab equipment was used in ZY-102 experiment?",
        domain="biotech",
        source_types=["email", "pdf"]
    )
    for i, res in enumerate(results, 1):
        print(f"📄 Result {i}:\n{res.strip()}\n{'-'*60}")