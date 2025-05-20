import os
import json
from pathlib import Path
import fitz  # PyMuPDF
from email import policy
from email.parser import BytesParser

def extract_pdf_text(path):
    with fitz.open(path) as doc:
        return "".join([page.get_text() for page in doc])

def extract_eml_content(path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
        # return f"Subject: {msg['subject']}\n\n{msg.get_body(preferencelist=('plain')).get_content()}"
        return (
            f"From: {msg['from']}\n"
            f"To: {msg['to']}\n"
            f"Subject: {msg['subject']}\n\n"
            f"{msg.get_body(preferencelist=('plain')).get_content()}"
        )

def parse_documents(base_dir, output_file):
    output = []
    base_path = Path(base_dir)

    for domain_dir in base_path.iterdir():
        if domain_dir.is_dir():
            domain = domain_dir.name  # e.g., biotech, energy, finance
            for file_path in domain_dir.iterdir():
                try:
                    if file_path.suffix == ".pdf":
                        text = extract_pdf_text(file_path)
                    elif file_path.suffix == ".eml":
                        text = extract_eml_content(file_path)
                    else:
                        continue

                    output.append({
                        "file": file_path.name,
                        "text": text,
                        "domain": domain
                    })

                except Exception as e:
                    print(f"❌ Error parsing {file_path.name}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        for doc in output:
            f.write(json.dumps(doc) + "\n")

    print(f"✅ Parsed {len(output)} documents into {output_file}")

if __name__ == "__main__":
    parse_documents("data/unstructured", "data/unstructured/parsed.jsonl")