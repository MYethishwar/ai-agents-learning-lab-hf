"""
The GAIA agent.

Flow for one question:

    question (+ attached file)
        -> open the attachment          (attachments.py)
        -> CodeAgent thinks, writes Python, calls tools, repeats  (smolagents)
        -> final_answer(...)
        -> clean the answer so it passes an exact-match check
"""

import re
from pathlib import Path

from smolagents import CodeAgent, OpenAIServerModel

import scoring_api
from attachments import load_attachment
from llm import GEMINI_API_KEY, GEMINI_BASE_URL, MODEL_ID, REQUESTS_PER_MINUTE
from tools import build_tools

FILES_DIR = Path("downloads")
MAX_STEPS = 12

# GAIA's answer rules, adapted for this course (no "FINAL ANSWER:" prefix).
INSTRUCTIONS = """\
You are solving questions from the GAIA benchmark. Your answer is compared to the correct one by EXACT MATCH.

How to work:
- Find facts with your tools instead of guessing. Check the source page, not just the search snippet.
- Web pages are long. Find a keyword in the page text (e.g. text.find("Studio albums")) and print the
  text around it, then read it yourself. Don't trust a regex or parser that found nothing: look at the text.
- If the question names a specific source or version (e.g. "2022 English Wikipedia"), use that source.
- Read the question carefully: some are puzzles (e.g. reversed text) and need no tools at all.

How to answer: call final_answer with ONLY the answer, nothing else.
- A number: digits only, no thousands separators, no units or symbols ($, %) unless the question asks for them.
- A word or name: as few words as possible, no articles, no abbreviations (write city names in full).
- A list: comma separated with one space after each comma, e.g. "a, b, c". Apply the rules above to each item.
- Follow every format the question asks for: alphabetical or ascending order, decimals, first name only,
  last names only, IOC code, algebraic chess notation, and so on.
- No explanation, no full sentence, no trailing period.
"""


class GaiaAgent:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise RuntimeError("Set GEMINI_API_KEY. Get a free key at https://aistudio.google.com/apikey")
        self.agent = CodeAgent(
            tools=build_tools(),
            model=OpenAIServerModel(
                model_id=MODEL_ID,
                api_base=GEMINI_BASE_URL,
                api_key=GEMINI_API_KEY,
                requests_per_minute=REQUESTS_PER_MINUTE,
            ),
            instructions=INSTRUCTIONS,
            # Python modules the agent's own code may import (math, re, datetime ... are allowed by default).
            additional_authorized_imports=["pandas", "numpy"],
            max_steps=MAX_STEPS,
        )
        print(f"GaiaAgent ready: {MODEL_ID}")

    def __call__(self, question: str, task_id: str = "", file_name: str = "") -> str:
        task = question
        images = None

        if file_name:
            path = scoring_api.download_file(task_id, file_name, FILES_DIR)
            attachment = load_attachment(path)
            task = f"{question}\n\n{attachment.text}"
            images = attachment.images or None

        answer = self.agent.run(task, images=images)
        return clean_answer(answer)


def clean_answer(answer) -> str:
    """Make the agent's final answer safe for an exact-match check."""
    if isinstance(answer, (list, tuple)):
        answer = ", ".join(str(item) for item in answer)
    text = str(answer).strip()
    text = re.sub(r"^final answer\s*:\s*", "", text, flags=re.IGNORECASE)  # in case the model adds it anyway
    text = text.strip().strip("\"'").strip()
    text = re.sub(r"\s*,\s*", ", ", text)  # lists: always "a, b, c"
    return text.rstrip(".")
