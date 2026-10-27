"""Last step for every question: make the agent's answer safe for an exact-match check."""

import re


def clean_answer(answer) -> str:
    """Make the agent's final answer safe for an exact-match check."""
    if isinstance(answer, (list, tuple)):
        answer = ", ".join(str(item) for item in answer)
    text = str(answer).strip()
    text = re.sub(r"^final answer\s*:\s*", "", text, flags=re.IGNORECASE)  # in case the model adds it anyway
    text = text.strip().strip("\"'").strip()
    text = re.sub(r"\s*,\s*", ", ", text)  # lists: always "a, b, c"
    return text.rstrip(".")
