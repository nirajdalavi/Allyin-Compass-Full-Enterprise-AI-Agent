import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Step 1: Load parsed data
with open("data/unstructured/parsed.jsonl", "r", encoding="utf-8") as f:
    raw_docs = [json.loads(line) for line in f]

# Step 1.5: Chunk the documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
docs = []
for doc in raw_docs:
    chunks = text_splitter.split_text(doc["text"])
    for chunk in chunks:
        docs.append({
            "text": chunk,
            "file": doc["file"],
            "domain": doc.get("domain", "general"),
            "source_type": "email" if doc["file"].lower().endswith(".eml") else "pdf"
        })

texts = [doc["text"] for doc in docs]

# Step 2: Generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts)

# Step 3: Connect to Qdrant
client = QdrantClient("localhost", port=6333)

# Step 4: Create a collection (if it doesn't exist)
client.recreate_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE),
)

# Step 5: Upload points
points = []
for i, (text, embedding) in enumerate(zip(texts, embeddings)):
    points.append(
        PointStruct(
            id=int(hashlib.md5(text.encode()).hexdigest()[:8], 16),
            vector=embedding.tolist(),
            payload={
                "text": text,
                "source_file": docs[i]["file"].lower(),
                "domain": docs[i].get("domain", "general"),
                "source_type": docs[i]["source_type"]
            }
        )
    )

client.upsert(collection_name="docs", points=points)

print(f"✅ Uploaded {len(points)} embedded chunks to Qdrant.")