import json
import os
from datetime import datetime

def log_feedback(query, answer, rating, domain=None, tool_used=None, timestamp = None,response_time=None):
    log = {
        "query": query,
        "answer": answer,
        "rating": rating,
        "domain": domain,
        "tool_used": tool_used,
        "timestamp": timestamp,
        "response_time": response_time,

    }

    # Path to the same folder where logger.py exists (i.e., src/feedback/)
    current_dir = os.path.dirname(__file__)
    log_path = os.path.join(current_dir, "feedback_log.jsonl")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")

    print(f"✅ Logged feedback to {log_path}")