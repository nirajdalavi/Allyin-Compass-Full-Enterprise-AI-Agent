import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from retrievers.sql_retriever import get_sql_answer
from retrievers.vector_retriever import query_vector_db
from retrievers.graph_retriever import get_graph_facts
import streamlit as st
# --- Load environment variables ---
load_dotenv()

# --- Set up OpenRouter LLM via ChatOpenAI wrapper ---
llm = ChatOpenAI(
    temperature=0,
    model="mistralai/mistral-7b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

# --- Wrapper for logging ---
def log_tool_call(tool_name):
    print(f"🛠 Tool Used: {tool_name} | 🕒 {time.strftime('%H:%M:%S')}")

# --- Define each tool wrapper ---

def sql_tool_fn(question: str) -> str:
    log_tool_call("SQL Retriever")
    st.session_state["last_tool"] = "SQLTool"
    result = get_sql_answer(question)
    st.session_state["highlight_chunks"] = [result]  # Store SQL output for UI highlight display
    return result



# def vector_tool_fn(question: str, domain=None) -> str:
#     chunks = query_vector_db(question, domain=domain)
#     if not chunks:
#         return "No relevant documents found."

#     context = "\n\n".join(chunks)
#     prompt = f"""Use the following document content to answer the question.

# Document:
# {context}

# Question: {question}
# Answer:"""
    
#     return llm.invoke(prompt).content
def vector_tool_fn(question: str, domain=None, confidence_threshold=0.0) -> str:
    st.session_state["last_tool"] = "VectorTool"
    # chunks = query_vector_db(question, domain=domain, confidence_threshold=confidence_threshold)
    chunks = query_vector_db(
    question,
    domain=domain,
    confidence_threshold=confidence_threshold,
    source_types=["pdf", "email"]
)

    if not chunks:
        return "No relevant documents found."

    st.session_state["highlight_chunks"] = chunks  # Save for UI highlighting

    context = "\n\n".join(chunks)
    # context = "\n\n".join([c["text"] for c in chunks])
    prompt = f"""Use the following document content to answer the question.

Document:
{context}

Question: {question}
Answer:"""

    return llm.invoke(prompt).content


import re

def normalize(text: str) -> set:
    return set(re.findall(r"\w+", text.lower()))

def graph_tool_fn(question: str) -> str:
    print("📥 graph_tool_fn received:", question)
    st.session_state["last_tool"] = "GraphTool"
    graph_data = get_graph_facts()
    q_tokens = normalize(question)
    matches = []

    for d in graph_data:
        # Combine all tokens in triple
        triple = f"{d['from']} {d['relation']} {d['to']}"
        triple_tokens = normalize(triple)

        # Strong match: question overlaps with both from and to tokens
        if (q_tokens & normalize(d['from']) and q_tokens & normalize(d['to'])) or (q_tokens & triple_tokens):
            matches.append(triple)

    print("📤 Filtered matches:", matches)
    st.session_state["highlight_chunks"] = matches  # Allow app.py to display matched triples
    return "\n".join(matches) or "No graph matches found. Consider retrying with a document-based tool like VectorTool."

# --- Register tools for the agent ---



def get_tools(selected_domain=None, source_filter=None, confidence_threshold=0.0):
    tools = []

    if not source_filter or "sql" in source_filter:
        tools.append(
                Tool(
        name="SQLTool",
        func=sql_tool_fn,
       description="""
Use this tool to answer questions using structured enterprise data from DuckDB.

Available tables and their schemas:

- `customers(customer_id, name, email, country, account_balance, last_transaction_date)`
  → Financial customer details including balances and locations.

- `emissions(facility_id, facility_name, co2_emissions_tons, reporting_year)`
  → Environmental data: CO2 emissions reported annually by each facility.

- `orders(order_id, customer_id, product, amount, order_date)`
  → Biotech domain orders placed by customers.

- `compliance_report(file, emails, phone_numbers, compliance_risks)`
  → Security and compliance metadata extracted from unstructured documents.
  - Detected compliance risks and PII in documents


🧠 Tips for interpreting questions:
- If the question mentions **plants** like "Plant A", always filter using `facility_name` from the `emissions` table.

📌 Example query for product orders by Plant A:
```sql
SELECT o.product
FROM orders o
JOIN emissions e ON o.customer_id = e.facility_id
WHERE e.facility_name = 'Plant A';
    """,
    )
        )

    if not source_filter or "pdf/emails" in source_filter:
        tools.append(
               Tool(
        name="VectorTool",
        func=lambda q: vector_tool_fn(q, domain = selected_domain, confidence_threshold=confidence_threshold),
    description="""
Use this tool to answer questions from unstructured documents like PDFs and emails, stored in the vector database (Qdrant).

The documents include:
- Biotech: Molecule research summaries, lab memos, experiment protocols
- Energy: Emissions audits, regulatory notices, plant compliance updates
- Finance: Financial memos, client risk alerts, performance reports

Use this tool when:
- The question refers to reports, procedures, summaries, lab equipment, timelines, or audit findings
- The answer needs deep semantic understanding
- Examples:
  - "What lab equipment supported the ZY-102 experiment?"
  - "What did the audit say about CO2 limits?"
  - "What client accounts were flagged in India?"

This tool does NOT use structured databases or graphs — it only retrieves content from `.pdf` and `.eml` files.
    """,
return_direct = True

    )
        )

    if not source_filter or "graph" in source_filter:
        tools.append(
            Tool(
        name="GraphTool",
        func=graph_tool_fn,
      description="""
Use this tool to answer questions by querying the **enterprise knowledge graph** stored in Neo4j.
Use this tool to answer *specific factual queries* about known relationships in the enterprise knowledge graph (Neo4j).
The graph spans **multiple domains** with entities and relationships like:

 **Energy**
- `Facility` — nodes like "Plant A", "Plant B", etc.
- `Regulation` — e.g., "CO2 Limit", "Water Usage"
- Relationships: `EXCEEDS`, `COMPLIES_WITH`

 **Biotech**
- `ResearchLab` — e.g., "Lab X", "Lab Y"
- `Molecule`, `Paper` — e.g., "ZY-102", "Cancer Immunotherapy Results"
- Relationships: `RESEARCHES`, `PUBLISHED`

 **Finance**
- `Client`, `RiskCategory`, `Auditor`
- Relationships: `ASSESSED_FOR`, `FLAGGED_BY`

Use this tool to retrieve structured entity relationships from the enterprise knowledge graph (Neo4j).

The graph contains:
- Entities: Research Labs, Clients, Facilities, Molecules, Regulations
- Relations: RESEARCHES, PUBLISHED, EXCEEDS, COMPLIES_WITH, FLAGGED_BY, ASSESSED_FOR

Only use this tool to:
- Answer relationship-style queries like:
  - "Which lab researched ZY-102?"
  - "What molecule did Lab Z work on?"
  - "Which clients were flagged by auditors?"

This tool returns results in the form of:
<Entity A> <RELATION> <Entity B>

IMPORTANT: Do NOT use this tool for questions about document content, lab procedures, audit results, emails, or equipment. Use VectorTool instead for that type of context.
""",
    )
        )

    return tools

# --- Initialize the agent ---
agent = initialize_agent(
    tools=get_tools(),
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# --- Test input ---
if __name__ == "__main__":
    # query = "What regulation does Plant A exceed and what products were ordered?"
    # query = "What regulation does Plant C exceed and what products were ordered?"
    # query = "When will new CO2 regulations be effective?"
    query = "What lab is researching on molecules?"
 


    print(f"\n🤖 Agent Prompt: {query}")
    response = agent.run(query)
    print(f"\n🧠 Agent Response:\n{response}")