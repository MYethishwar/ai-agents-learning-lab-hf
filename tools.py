"""
Tools the agent can call while it works.

Each question was checked by hand to see what it really needs:

    web_search      (built-in)  find pages: Wikipedia, baseball stats, papers, articles ...  (~13 questions)
    visit_webpage      (ours)   read a page found by search, as markdown                     (same questions)
    youtube_transcript (ours)   read what is said in a YouTube video                         (Teal'c question)

Why our own visit_webpage instead of the built-in one:
    - Wikipedia answers 403 Forbidden unless the request has a descriptive User-Agent.
    - The built-in tool cuts long pages, which can drop the part we need (e.g. a discography
      at the end of a Wikipedia article). We return the whole page: in a CodeAgent the result
      is a Python string, so the agent can search it in code instead of printing all of it.

Everything else needs no tool:
    - reasoning / logic questions are solved by the model, or with Python code (CodeAgent runs code)
    - attachments are already opened for the agent (see attachments.py)
"""

import re

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from smolagents import DuckDuckGoSearchTool, tool
from youtube_transcript_api import YouTubeTranscriptApi

USER_AGENT = "GaiaAgent/1.0 (Hugging Face Agents Course student project) python-requests"


@tool
def visit_webpage(url: str) -> str:
    """Download a webpage and return its full content as markdown.
    Pages can be long: store the result in a variable and search it in code
    (e.g. find a section title) instead of printing everything.

    Args:
        url: The URL of the webpage to read.
    """
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        return f"Error fetching the webpage: {error}"

    # Keep only the main content: drop menus, sidebars and scripts, which are noise for the agent.
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    content = soup.find("main") or soup.body or soup

    markdown = markdownify(str(content)).strip()
    return re.sub(r"\n{3,}", "\n\n", markdown)  # collapse runs of blank lines


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


def build_tools() -> list:
    return [
        DuckDuckGoSearchTool(max_results=8),
        visit_webpage,
        youtube_transcript,
    ]
