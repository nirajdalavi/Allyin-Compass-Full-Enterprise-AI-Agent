def tag_compliance_risks(text: str) -> list:
    """
    Flag compliance-sensitive keywords. Can be expanded per domain.
    """
    risk_keywords = [
        "restatement",
        "earnings risk",
        "compliance breach",
        "data leak",
        "exceeded limit",
        "regulatory audit",
        "unauthorized access",
        "violation",
        "threshold breach",
        "non-compliance"
    ]

    found = [kw for kw in risk_keywords if kw.lower() in text.lower()]
    return found