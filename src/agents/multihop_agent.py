from multi_tool_agent import get_tools, llm
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# Setup LLM




ReActPrompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question: {input}
{agent_scratchpad}
""")

# Get tools from your existing function
tools = get_tools(selected_domain="biotech", source_filter=None, confidence_threshold=0.5)

# Create agent
agent = create_react_agent(llm=llm, tools=tools, prompt=ReActPrompt)

# Wrap in executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)


def format_multihop_answer(result):
    steps = result.get("intermediate_steps", [])
    final_obs = steps[-1][1].strip() if steps else "No answer found."

    lines = ["🧠 Final Answer:\n", final_obs, "\n"]

    # Show trace (optional)
    lines.append("🔍 Trace:\n")
    for action, obs in steps:
        lines.append(f"- 🛠 {action.tool}: *{action.tool_input}*")
        lines.append(f"  → {obs.strip()}\n")

    return "\n".join(lines)


# Run it
result = agent_executor.invoke({"input": "Which clients were flagged in risk memos and what are their account balances?"})
print(format_multihop_answer(result))