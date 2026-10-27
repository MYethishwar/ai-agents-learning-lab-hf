"""
visit_webpage: read a page found by search, as markdown.

Why our own tool instead of smolagents' built-in VisitWebpageTool:
    - Wikipedia answers 403 Forbidden unless the request has a descriptive User-Agent.
    - The built-in tool cuts long pages, which can drop the part we need (e.g. a discography
      at the end of a Wikipedia article). We return the whole page: in a CodeAgent the result
      is a Python string, so the agent can search it in code instead of printing all of it.
"""

import re

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from smolagents import tool

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
