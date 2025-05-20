import re

def detect_pii(text: str) -> dict:
    """Detect basic PII like emails and phone numbers in a given text."""
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phones = re.findall(r"\b(?:\+?\d{1,2}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)

    return {
        "emails": emails,
        "phone_numbers": phones
    }