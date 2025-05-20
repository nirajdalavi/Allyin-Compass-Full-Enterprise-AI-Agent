# import json
# from pii_filter import detect_pii
# from compliance_tagger import tag_compliance_risks

# def scan_documents(jsonl_path):
#     with open(jsonl_path, "r", encoding="utf-8") as f:
#         for line in f:
#             doc = json.loads(line)
#             text = doc["text"]

#             pii = detect_pii(text)
#             risks = tag_compliance_risks(text)

#             print(f"\n📄 File: {doc['file']}")
#             if pii["emails"] or pii["phone_numbers"]:
#                 print(f"⚠️  PII Detected:\n  Emails: {pii['emails']}\n  Phones: {pii['phone_numbers']}")
#             else:
#                 print("✅ No PII found.")

#             if risks:
#                 print(f"🚨 Compliance Risks Found: {risks}")
#             else:
#                 print("✅ No compliance risks.")

# if __name__ == "__main__":
#     scan_documents("data/unstructured/parsed.jsonl")

import json
import csv
from pii_filter import detect_pii
from compliance_tagger import tag_compliance_risks

def scan_documents(jsonl_path, output_csv_path):
    rows = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            text = doc["text"]
            filename = doc["file"]

            pii = detect_pii(text)
            risks = tag_compliance_risks(text)

            print(f"\n📄 File: {filename}")
            if pii["emails"] or pii["phone_numbers"]:
                print(f"⚠️  PII Detected:\n  Emails: {pii['emails']}\n  Phones: {pii['phone_numbers']}")
            else:
                print("✅ No PII found.")

            if risks:
                print(f"🚨 Compliance Risks Found: {risks}")
            else:
                print("✅ No compliance risks.")

            rows.append({
                "file": filename,
                "emails": ", ".join(pii["emails"]),
                "phone_numbers": ", ".join(pii["phone_numbers"]),
                "compliance_risks": ", ".join(risks)
            })

    # Write to CSV
    with open(output_csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["file", "emails", "phone_numbers", "compliance_risks"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ CSV report written to {output_csv_path}")

if __name__ == "__main__":
    scan_documents("data/unstructured/parsed.jsonl", "data/structured/compliance_report.csv")