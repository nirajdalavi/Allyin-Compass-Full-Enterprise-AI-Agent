import json

INPUT_FILE = "src/feedback/feedback_log.jsonl"
OUTPUT_FILE = "src/feedback/finetune_data.jsonl"

def format_feedback():
    formatted = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if data.get("rating") == 1:
                prompt = f"User Query: {data['query']}\n\nAnswer:"
                completion = f" {data['answer'].strip()}"
                formatted.append({
                    "prompt": prompt,
                    "completion": completion
                })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in formatted:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Saved {len(formatted)} formatted examples to {OUTPUT_FILE}")

if __name__ == "__main__":
    format_feedback()