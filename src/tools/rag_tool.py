import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI

# --- Load environment variables ---
load_dotenv()

# --- Initialize vector client and model ---
client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Configure LLM (OpenRouter-compatible) ---
llm = ChatOpenAI(
    temperature=0,
    model="mistralai/mistral-7b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)

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
    prompt = f"""You are a helpful assistant. Use the following information to answer the question.

Context:
{context}

Question: {query}
Answer:"""

    # Step 5: Call the LLM
    response = llm.invoke(prompt)
    return response, documents

# --- CLI test ---
if __name__ == "__main__":
    user_query = input("❓ Ask a question: ")
    answer, sources = answer_question_with_rag(user_query)

    print("\n🧠 Answer:\n", answer)
    print("\n📚 Sources:")
    for i, src in enumerate(sources, 1):
        print(f" {i}. {src[:100]}...")