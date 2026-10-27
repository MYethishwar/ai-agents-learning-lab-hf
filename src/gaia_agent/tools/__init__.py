"""
Tools the agent can call while it works.

Each question was checked by hand to see what it really needs:

    web_search         (built-in)    find pages: Wikipedia, baseball stats, papers, articles ...  (~13 questions)
    visit_webpage      web_page.py   read a page found by search, as markdown                     (same questions)
    youtube_transcript youtube.py    read what is said in a YouTube video                         (Teal'c question)

Everything else needs no tool:
    - reasoning / logic questions are solved by the model, or with Python code (CodeAgent runs code)
    - attachments are already opened for the agent (see gaia_agent.attachments)
"""

from smolagents import DuckDuckGoSearchTool

from gaia_agent.tools.web_page import visit_webpage
from gaia_agent.tools.youtube import youtube_transcript


def build_tools() -> list:
    return [
        DuckDuckGoSearchTool(max_results=8),
        visit_webpage,
        youtube_transcript,
    ]
