"""
Turn a question's attached file into something the LLM can read.

A human solving these questions would open the attachment first, then think.
We do the same, before the agent starts:

    .png / .jpg   -> a PIL image, passed to the model as vision input   (chess position)
    .mp3          -> a text transcript made by Gemini                  (pie recipe, homework pages)
    .py           -> the source code as text                           (final numeric output)
    .xlsx / .csv  -> the table as text, plus the path so pandas can load it   (menu sales)

Only these file types appear in the 20 questions, so nothing else is handled.
"""

import base64
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from openai import OpenAI
from PIL import Image

from llm import GEMINI_API_KEY, GEMINI_BASE_URL, MODEL_ID


@dataclass
class Attachment:
    """What the agent gets from one attached file."""

    text: str = ""  # added to the prompt
    images: list = field(default_factory=list)  # passed to the model as images


def load_attachment(path: Path) -> Attachment:
    suffix = path.suffix.lower()

    if suffix in (".png", ".jpg", ".jpeg"):
        return Attachment(
            text=f"The attached image ({path.name}) is provided to you as an image input.",
            images=[Image.open(path).convert("RGB")],
        )

    if suffix == ".mp3":
        transcript = transcribe_audio(path)
        return Attachment(text=f"Transcript of the attached audio file ({path.name}):\n{transcript}")

    if suffix == ".py":
        code = path.read_text(encoding="utf-8")
        return Attachment(text=f"Content of the attached Python file ({path.name}):\n```python\n{code}\n```")

    if suffix in (".xlsx", ".xls", ".csv"):
        table = pd.read_csv(path) if suffix == ".csv" else pd.read_excel(path)
        return Attachment(
            text=(
                f"The attached spreadsheet is saved at: {path.as_posix()}\n"
                f"You can load it in code with pandas. Its full content is:\n{table.to_string()}"
            )
        )

    # Any other file type: just tell the agent where it is.
    return Attachment(text=f"An attached file is saved at: {path.as_posix()}")


def transcribe_audio(path: Path) -> str:
    """Speech-to-text: send the audio to Gemini and ask for a word-for-word transcript."""
    client = OpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
    audio = base64.b64encode(path.read_bytes()).decode("utf-8")
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Transcribe this audio word for word. Reply with the transcript only."},
                    {"type": "input_audio", "input_audio": {"data": audio, "format": "mp3"}},
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()
