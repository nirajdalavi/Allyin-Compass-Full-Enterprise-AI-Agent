# import os
# import re
# from dotenv import load_dotenv
# from langchain_community.utilities.sql_database import SQLDatabase
# from langchain_community.chat_models import ChatOpenAI
# from langchain_experimental.sql import SQLDatabaseChain

# def clean_sql(raw_sql: str) -> str:
#     # Remove Markdown code block formatting like ```sql ... ```
#     cleaned = re.sub(r"```(?:sql)?\s*([\s\S]+?)\s*```", r"\1", raw_sql.strip())
#     return cleaned.strip("`").strip()

# load_dotenv()

# llm = ChatOpenAI(
#     temperature=0,
#     openai_api_base="https://openrouter.ai/api/v1",
#     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
#     model="mistralai/mistral-7b-instruct"
# )

# db = SQLDatabase.from_uri("duckdb:///allyin.db")

# db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True, return_intermediate_steps=True)

# question = "What is the total order amount?"

# # ✅ Let the chain run fully
# response = db_chain.invoke({"query": question})

# # Extract and clean the SQL
# intermediates = response.get("intermediate_steps", [])
# if intermediates:
#     raw_sql = intermediates[-1]
#     sql_cleaned = clean_sql(raw_sql)

#     print("🧠 Raw SQL:", raw_sql)
#     print("✅ Cleaned SQL:", sql_cleaned)

#     # Execute the cleaned SQL
#     try:
#         result = db.run(sql_cleaned)
#         print("\n🧠 Final Answer:", result)
#     except Exception as e:
#         print("❌ SQL Execution Error:", e)
# else:
#     print("⚠️ No intermediate SQL found.")


# def get_sql_answer(question: str) -> str:
#     import os
#     from dotenv import load_dotenv
#     from langchain_community.utilities.sql_database import SQLDatabase
#     # from langchain_community.chat_models import ChatOpenAI
#     from langchain.chains.sql_database.query import create_sql_query_chain
#     from langchain_openai import ChatOpenAI


#     # --- Load environment variables ---
#     load_dotenv()

#     # --- Connect to DuckDB ---
#     db = SQLDatabase.from_uri("duckdb:///allyin.db")

#     # --- Set up OpenRouter LLM ---
#     llm = ChatOpenAI(
#         temperature=0,
#         model="mistralai/mistral-7b-instruct",
#         openai_api_base="https://openrouter.ai/api/v1",
#         openai_api_key=os.getenv("OPENROUTER_API_KEY")
#     )

#     # Create chain normally (no include_answer param)
#     sql_chain = create_sql_query_chain(llm, db)

#     # Ask your question
#     question = "What is the total order amount?"
#     llm_response = sql_chain.invoke({"question": question})

#     # Manually extract SQL line from response
#     import re
#     match = re.search(r"(?i)SQLQuery:\s*(.+)", llm_response)
#     if match:
#         sql_only = match.group(1).strip().strip("`")
#     else:
#         sql_only = llm_response.strip()

#     print("🧠 LLM Response:\n", llm_response)
#     print("\n✅ Extracted SQL:\n", sql_only)

#     # Execute the SQL
#     try:
#         result = db.run(sql_only)
#         print("\n✅ Final Answer:", result)
#     except Exception as e:
#         print("❌ SQL Execution Error:", e)

# get_sql_answer()


import os
import re
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_openai import ChatOpenAI

# --- Load environment variables ---
load_dotenv()

# --- Connect to DuckDB ---
db = SQLDatabase.from_uri("duckdb:///allyin.db")

# --- Set up OpenRouter-compatible LLM ---
llm = ChatOpenAI(
    temperature=0,
    model="mistralai/mistral-7b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY")
)

# --- Create SQL chain ---
sql_chain = create_sql_query_chain(llm, db)

# --- SQL cleaner utility ---
# def clean_sql_response(response: str) -> str:
#     """
#     Extracts SQL from LLM output. Removes SQLQuery label, markdown code blocks, and backticks.
#     """
#     response = re.sub(r"```(?:sql)?\s*([\s\S]+?)\s*```", r"\1", response)
#     response = re.sub(r"(?i)SQLQuery:\s*", "", response)
#     return response.strip().strip("`").strip()
def clean_sql_response(response: str) -> str:
    """
    Extracts just the SQL part from LLM responses.
    Removes explanation text, markdown, and extra lines.
    """
    # First try to extract from a markdown block
        # Remove markdown code blocks like ```sql ... ```
    response = re.sub(r"```(?:sql)?\s*([\s\S]+?)\s*```", r"\1", response)

    # Remove inline backticks and SQLQuery: prefix
    response = re.sub(r"(?i)SQLQuery:\s*", "", response)
    response = response.replace("`", "")

    # Extract only from the first SELECT/WITH onward if explanation exists
    lines = response.strip().splitlines()
    for i, line in enumerate(lines):
        if line.strip().upper().startswith(("SELECT", "WITH")):
            return "\n".join(lines[i:]).strip()

    # Fallback to cleaned response
    return response.strip()

# --- Main function to ask a question and run SQL ---
def get_sql_answer(question: str) -> str:
    if question.lower().startswith("select"):
        sql_only = question.strip().strip("`")
    else:
        llm_response = sql_chain.invoke({"question": question})
        print("🧠 LLM Response:\n", llm_response)
        sql_only = clean_sql_response(llm_response)

    print("\n✅ Extracted SQL:\n", sql_only)

    # try:
    #     result = db.run(sql_only)
    #     return str(result[0][0]) if result and isinstance(result[0], (tuple, list)) else str(result)
    # except Exception as e:
    #     return f"❌ SQL Execution Error: {e}"
    try:
        result = db.run(sql_only)
        if result and isinstance(result, list):
            result_str = ", ".join([str(row[0]) for row in result])
            return f"The result is: {result_str}"
        return str(result)
    except Exception as e:
        return f"❌ SQL Execution Error: {e}"

# --- Test block ---
if __name__ == "__main__":
    # question = "What is the total account balance of customers?"
    question = "What countries are the customers from?"

    answer = get_sql_answer(question)
    print("\n✅ Final Answer:", answer)
