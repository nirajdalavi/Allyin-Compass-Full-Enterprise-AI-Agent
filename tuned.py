from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from peft import PeftModel
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import torch

# Load tokenizer and base model
base_model_id = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_id)

# Load the LoRA adapter
adapter_path = "models/lora_adapter"
model = PeftModel.from_pretrained(base_model, adapter_path)
model.eval()

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Qdrant
client = QdrantClient("localhost", port=6333)

# Inference function using RAG style
def run_rag_inference(query: str, domain: str = None, top_k: int = 3):
    # Step 1: Embed the query
    query_vec = embed_model.encode(query).tolist()

    # Step 2: Search Qdrant
    search_filter = None
    if domain:
        search_filter = Filter(
            must=[FieldCondition(key="domain", match=MatchValue(value=domain))]
        )

    hits = client.search(
        collection_name="docs",
        query_vector=query_vec,
        limit=top_k,
        query_filter=search_filter,
    )

    # Step 3: Combine context
    context = "\n\n".join(hit.payload["text"] for hit in hits)

    # Step 4: Generate answer using LoRA model
    prompt = f"""You are an expert assistant. Use the context below to answer the question in a complete sentence.

Context:
{context}

### Question:
{query}

### Answer:
"""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True), hits


if __name__ == "__main__":
    query = " What lab equipment supported ZY-102?"
    answer, sources = run_rag_inference(query, domain="biotech")

    print("🧠 Answer:\n", answer.strip())
    print("\n📚 Sources:")
    for i, hit in enumerate(sources, 1):
        print(f"{i}. {hit.payload['text'][:300].strip()}...\n")