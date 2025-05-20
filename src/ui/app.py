import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from agents.multi_tool_agent import get_tools
from agents.multi_tool_agent import sql_tool_fn
from agents.multi_tool_agent import vector_tool_fn
from agents.multi_tool_agent import graph_tool_fn


from dashboards.metrics import display_dashboard



from retrievers.sql_retriever import get_sql_answer
from retrievers.vector_retriever import query_vector_db
from retrievers.graph_retriever import get_graph_facts

from langchain.agents import Tool, initialize_agent
from langchain_openai import ChatOpenAI

# --- Load environment variables ---
load_dotenv()

# --- Define individual tool wrappers ---
# def sql_tool_fn(question: str) -> str:
#     st.session_state["last_tool"] = "SQLTool"
#     return get_sql_answer(question)

# # def vector_tool_fn(question: str, domain: str = None) -> str:
# #     chunks = query_vector_db(question, top_k=3, domain=None if domain == "general" else domain)
# #     return "\n\n".join(chunks)
# def vector_tool_fn(question: str, domain=None, confidence=0.0) -> str:
#     st.session_state["last_tool"] = "VectorTool"
#     chunks = query_vector_db(question, domain=domain, confidence_threshold=confidence)
#     if not chunks:
#         return "No relevant documents found."

#     context = "\n\n".join(chunks)
#     prompt = f"""You are an expert assistant extracting factual answers from internal documents. 
# Match semantically equivalent phrases. For example, "did the research" may correspond to "prepared by", "lead scientist", or "conducted trials".

# Document:
# {context}

# Question:
# {question}

# Answer:"""
    
#     return llm.invoke(prompt).content



# import re
# def normalize(text: str) -> set:
#     return set(re.findall(r"\w+", text.lower()))

# def graph_tool_fn(question: str) -> str:
#     st.session_state["last_tool"] = "GraphTool"
#     print("📥 graph_tool_fn received:", question)
#     graph_data = get_graph_facts()
#     q_tokens = normalize(question)
#     matches = []

#     for d in graph_data:
#         # Combine all tokens in triple
#         triple = f"{d['from']} {d['relation']} {d['to']}"
#         triple_tokens = normalize(triple)

#         # Strong match: question overlaps with both from and to tokens
#         if (q_tokens & normalize(d['from']) and q_tokens & normalize(d['to'])) or (q_tokens & triple_tokens):
#             matches.append(triple)

#     print("📤 Filtered matches:", matches)
#     return "\n".join(matches) or "No matches found."

# --- Setup LLM ---
llm = ChatOpenAI(
    temperature=0,
    model="mistralai/mistral-7b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)

# --- Setup tools ---
# tools = [
#     Tool(name="SQLTool", func=sql_tool_fn, description="Use this tool for structured data like orders, emissions, and customers."),
#     Tool(name="VectorTool", func=vector_tool_fn, description="Use this tool to answer questions from documents, emails, and PDFs."),
#     Tool(name="GraphTool", func=graph_tool_fn, description="Use this tool for facility-regulation relationships from the enterprise graph.")
# ]


# --- Streamlit UI ---
st.set_page_config(page_title="AllyIn Compass Assistant", layout="wide")
st.title("🤖 AllyIn Compass")
st.markdown("Ask your smart assistant anything across enterprise data.")

# --- Input area ---
query = st.text_input("❓ Ask a question:")
domain = st.selectbox("Select a domain:", ["general", "biotech", "finance", "energy"])

# --- Sidebar filters ---
st.sidebar.header("Filters")
confidence = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5)
st.sidebar.text("(Filters")
source_filter = st.sidebar.multiselect("📂 Filter by source type", ["sql","pdf/emails", "graph"])

# --- Dashboard section ---
st.sidebar.markdown("### 📊 Dashboard")
display_dashboard()

# --- Initialize Agent ---
selected = None if domain == "general" else domain

agent = initialize_agent(
    tools=get_tools(selected,source_filter= source_filter, confidence_threshold=confidence),
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

        


# --- Submit ---
if st.button("🧠 Run Query") and query:
    import time
    start_time = time.time()
    with st.spinner("Thinking..."):
        try:
            response = agent.run(query)
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            st.session_state["last_duration"] = duration
            st.session_state["last_query"] = query
            st.session_state["last_response"] = response
            st.session_state["query_ran"] = True

            st.success(f"Answer: {response}")
            st.caption(f"{duration}s")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Feedback Section (Always visible after query runs) ---
if st.session_state.get("query_ran", False):
    import time
    st.markdown("### Was this helpful?")
    col1, col2 = st.columns(2)
    from feedback.logger import log_feedback

    if col1.button("👍 Yes"):
        log_feedback(
            st.session_state["last_query"],
            st.session_state["last_response"],
            1,
            domain,
            tool_used=st.session_state.get("last_tool", "unknown"),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            response_time=st.session_state.get("last_duration", 0)
        )
        st.success("Thanks for the feedback!")
        st.rerun()

    if col2.button("👎 No"):
        log_feedback(
            st.session_state["last_query"],
            st.session_state["last_response"],
            0,
            domain,
            tool_used=st.session_state.get("last_tool", "unknown"),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            response_time=st.session_state.get("last_duration", 0)
        )
        st.info("Got it. We'll use this to improve.")
        st.rerun()
    # --- Highlight source text / facts if available ---
    if "highlight_chunks" in st.session_state and st.session_state["highlight_chunks"]:
        st.markdown("---")
        st.markdown("#### Source Information")
        for chunk in st.session_state["highlight_chunks"]:
            # st.markdown(f"**📄 {chunk['file']}**")
            st.code(chunk, language="text")
            