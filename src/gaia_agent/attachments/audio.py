"""Speech-to-text for .mp3 attachments, done by the same Gemini model the agent uses."""

import base64
from pathlib import Path

from gaia_agent.llm import MODEL_ID, chat_client


def transcribe_audio(path: Path) -> str:
    """Send the audio to Gemini and ask for a word-for-word transcript."""
    audio = base64.b64encode(path.read_bytes()).decode("utf-8")
    response = chat_client().chat.completions.create(
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
