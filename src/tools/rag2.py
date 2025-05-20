import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# --- Load environment variables ---
load_dotenv()

# --- Initialize vector client and model ---
client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Configure local Flan-T5 model ---
hf_model_id = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
t5_model = AutoModelForSeq2SeqLM.from_pretrained(hf_model_id)
llm_pipeline = pipeline("text2text-generation", model=t5_model, tokenizer=tokenizer)

# --- RAG function ---
def answer_question_with_rag(query: str, top_k=3):
    # Step 1: Embed the query
    vector = model.encode(query).tolist()

    # Step 2: Search Qdrant
    hits = client.search(
        collection_name="docs",
        query_vector=vector,
        limit=top_k
    )

    # Step 3: Combine top documents into context
    documents = [hit.payload["text"] for hit in hits]
    context = "\n---\n".join(documents)

    # Step 4: Build the prompt
    prompt = f"""You are an expert assistant. Use the context below to answer the question in a complete sentence.

Context:
{context}

Question: {query}
Answer:"""

    # Step 5: Generate response
    result = llm_pipeline(prompt, max_new_tokens=100, truncation=True)
    return result[0]["generated_text"].strip(), documents

# --- CLI test ---
if __name__ == "__main__":
    user_query = input("❓ Ask a question: ")
    answer, sources = answer_question_with_rag(user_query)

    print("\n🧠 Answer:\n", answer)
    print("\n📚 Sources:")
    for i, src in enumerate(sources, 1):
        print(f" {i}. {src[:100]}...")