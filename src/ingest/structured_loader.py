import duckdb
import pandas as pd
import os

# ✅ Connect to a persistent DB file
con = duckdb.connect("allyin.db")

def load_csv_to_duckdb(file_path, table_name):
    print(f"Loading {file_path} into DuckDB as table '{table_name}'...")
    df = pd.read_csv(file_path)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"✓ Loaded {len(df)} rows into '{table_name}'")

if __name__ == "__main__":
    base_path = "data/structured"
    
    if not os.path.exists(base_path):
        print("❌ Folder not found:", base_path)
        exit(1)

    for file_name in os.listdir(base_path):
        if file_name.endswith(".csv"):
            table_name = file_name.replace(".csv", "")
            file_path = os.path.join(base_path, file_name)
            load_csv_to_duckdb(file_path, table_name)

    # ✅ Preview
    print("\n📊 Tables in allyin.db:")
    print(con.execute("SHOW TABLES").fetchdf())

    print("\n📋 Sample from 'emissions':")
    print(con.execute("SELECT * FROM compliance_report LIMIT 6").fetchdf())