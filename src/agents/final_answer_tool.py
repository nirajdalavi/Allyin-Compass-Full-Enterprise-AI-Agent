# src/agents/final_answer_tool.py
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    temperature=0,
    model="mistralai/mistral-7b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)

def summarize_tool_fn(context: str) -> str:
    prompt = f"""You are a helpful assistant summarizing final answers from tool outputs.
Based on the following tool results, provide a clear and concise final answer.

Tool Outputs:
{context}

Final Answer:"""
    return llm.invoke(prompt).content

final_answer_tool = Tool(
    name="FinalAnswerTool",
    func=summarize_tool_fn,
    description="Use this tool to summarize the answer after all tool observations are complete."
)
