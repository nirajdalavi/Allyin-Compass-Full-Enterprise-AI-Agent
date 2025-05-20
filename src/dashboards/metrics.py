import os
import json
from datetime import datetime
from collections import Counter
import pandas as pd
import streamlit as st

# --- Load feedback logs ---
def load_feedback_logs(log_path="src/feedback/feedback_log.jsonl"):
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# --- Aggregate metrics ---
def compute_metrics(logs):
    queries_by_day = Counter()
    tool_usage = Counter()
    response_times = []

    for entry in logs:
        ts = entry.get("timestamp")
        if ts:
            day = datetime.fromisoformat(ts).date()
            queries_by_day[str(day)] += 1

        tool = entry.get("tool_used")
        if tool:
            tool_usage[tool] += 1

        rt = entry.get("response_time")
        if rt:
            response_times.append(rt)

    return queries_by_day, tool_usage, response_times

# --- Display metrics ---
def show_dashboard():
    logs = load_feedback_logs()
    if not logs:
        st.sidebar.warning("No feedback logs found.")
        return

    queries_by_day, tool_usage, response_times = compute_metrics(logs)

    st.sidebar.header("📊 Observability Dashboard")

    st.sidebar.subheader("Queries per Day")
    qdf = pd.DataFrame(queries_by_day.items(), columns=["Date", "Queries"]).sort_values("Date")
    st.sidebar.line_chart(qdf.set_index("Date"))

    st.sidebar.subheader("Tool Usage Frequency")
    tdf = pd.DataFrame(tool_usage.items(), columns=["Tool", "Usage"])
    st.sidebar.bar_chart(tdf.set_index("Tool"))

    st.sidebar.subheader("Average Response Time (s)")
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        st.sidebar.metric("Avg Time", f"{avg_time:.2f} s")
    else:
        st.sidebar.write("No timing data available.")

display_dashboard = show_dashboard