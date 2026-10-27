"""youtube_transcript: read what is said in a YouTube video (its captions)."""

import re

from smolagents import tool
from youtube_transcript_api import YouTubeTranscriptApi


@tool
def youtube_transcript(url: str) -> str:
    """Return the spoken text (captions) of a YouTube video.

    Args:
        url: The full YouTube video URL, e.g. https://www.youtube.com/watch?v=abc123
    """
    match = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    if not match:
        return f"Could not find a video id in: {url}"

    try:
        transcript = YouTubeTranscriptApi().fetch(match.group(1))
    except Exception as error:  # no captions, video blocked, network error ...
        return f"No transcript available for this video ({type(error).__name__})."

    # One line per caption, with its start time, so the agent can follow the conversation.
    return "\n".join(f"[{snippet.start:.0f}s] {snippet.text}" for snippet in transcript)
