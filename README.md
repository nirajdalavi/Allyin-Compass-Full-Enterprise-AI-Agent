0: Environment Setup
Goal: Prepare your system for development.
 	•	Installed required tools:
	•	Python 3.10+
	•	Docker Desktop
	•	VS Code
	•	Created project directory:
        mkdir -p allyin-compass/{src/ingest,data/structured}
        cd allyin-compass
        conda activate allyin
    •	Created a requirements.txt file
    •	Installed dependencies:
        pip install -r requirements.txt

1: Structured Data Loader
Goal: Ingest structured .csv files into DuckDB.
	•	Created 3 sample CSVs:
	•	customers.csv, orders.csv, emissions.csv
Saved in data/structured/.
	•	Created and ran structured_loader.py:
    python src/ingest/structured_loader.py

     File: src/ingest/structured_loader.py
	•	Loaded all .csv files from data/structured/
	•	Created DuckDB tables named after filenames


 2: Unstructured Data Ingestion (PDF + Email)
 Goal: Extract and structure text from PDFs and .eml files.
 	•	Created data/unstructured/ directory.
	•	Generated 3 sample PDFs and 3 .eml emails with realistic content.
    •	Created and ran document_parser.py:
        python src/ingest/document_parser.py
    File: src/ingest/document_parser.py
	    •	Extracted text from each .pdf and .eml
	    •	Saved parsed results to data/unstructured/parsed.jsonl, one line per document:
        {"file": "finance_report.pdf", "text": "Quarterly financial report..."}

3: Embedding and Vector Database
Goal: Convert documents into embeddings and store them in Qdrant.
	•	Started Qdrant (in Terminal 1):
        docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
    •	Created and ran embedder.py:
        python src/ingest/embedder.py
    File: src/ingest/embedder.py
	    •	Loaded parsed JSONL data
	    •	Generated embeddings using all-MiniLM-L6-v2
	    •	Uploaded vectors and metadata (text, source_file) into Qdrant under collection "docs"
    •	Created and ran vector_inspect.py to confirm storage:
        python src/ingest/vector_inspect.py
    File: src/ingest/vector_inspect.py
	    •	Retrieved and printed first few vectors.

4: Retrieval Systems (SQL + Vector + Graph)
Goal: Enable search across structured, unstructured, and relational data.

    SQL Retrieval
    • Installed additional dependencies:
    pip install langchain-experimental langchain-openai duckdb sqlalchemy
    • Created and ran sql_retriever.py:
    python src/retrievers/sql_retriever.py
    File: src/retrievers/sql_retriever.py
        • Connected to allyin.db using DuckDB + SQLAlchemy
        • Loaded mistralai/mistral-7b-instruct LLM via OpenRouter API
        • Used create_sql_query_chain() to convert natural language to SQL
        • Cleaned malformed SQL strings (e.g., backticks or markdown)
        • Executed SQL queries and returned answers from DuckDB

    Vector Retrieval
    • Created and ran vector_retriever.py:
        python src/retrievers/vector_retriever.py
    File: src/retrievers/vector_retriever.py
        • Loaded Qdrant client and all-MiniLM-L6-v2 model
        • Encoded input query as vector
        • Queried Qdrant for top 3 most relevant document chunks
        • Returned snippets from top matches using client.search()

    Graph Retrieval
    • Installed Neo4j Desktop and started a local database
    • Created and ran graph_retriever.py:
        python src/retrievers/graph_retriever.py
    File: src/retrievers/graph_retriever.py
        • Connected to Neo4j Bolt interface at bolt://localhost:7687
        • Created 10 sample nodes and edges:
        - Example:
        CREATE (:Facility {name: "Plant A"})-[:EXCEEDS]->(:Regulation {type: "CO2 Limit"})
        • Wrote get_violations() function to run Cypher queries
        • Returned results like: Plant A EXCEEDS CO2 Limit

5: Multi-Tool Agent with LangChain
Goal: Combine SQL, vector, and graph retrievers using an LLM agent.

    Tool Setup
    • Created custom functions:
    • get_sql_answer() → uses SQL chain
    • query_vector_db() → uses Qdrant
    • get_violations() → uses Neo4j
    • Wrapped each function using LangChain Tool()
    • Added clear description="" fields for LLM to understand tool usage

    Agent Setup
    • Created and ran multi_tool_agent.py:
        python src/agents/multi_tool_agent.py
    File: src/agents/multi_tool_agent.py
        • Imported all three tools
        • Initialized agent with initialize_agent([...], llm, agent_type="zero-shot-react-description")
        • Enabled verbose logging and timestamps for debugging
        • Agent parsed the user query and decided which tool(s) to invoke

    Sample Query
    • Prompt:
    "What regulation does Plant A exceed and what products were ordered?"
    
    • Execution Flow:
        1. GraphTool → returned: Plant A EXCEEDS CO2 Limit
        2. SQLTool → returned: Laptop (product ordered from Plant A)
        3. Combined final answer

