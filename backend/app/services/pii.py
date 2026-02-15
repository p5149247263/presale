import re


PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\+?\d[\d\-\s]{8,}\d\b"), "[REDACTED_PHONE]"),
]


def redact_pii(text: str) -> str:
    output = text
    for pattern, token in PII_PATTERNS:
        output = pattern.sub(token, output)
    return output
