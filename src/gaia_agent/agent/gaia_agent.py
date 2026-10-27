"""
The GAIA agent.

Flow for one question:

    question (+ attached file)
        -> open the attachment          (gaia_agent.attachments)
        -> CodeAgent thinks, writes Python, calls tools, repeats  (smolagents)
        -> final_answer(...)
        -> clean the answer so it passes an exact-match check     (answer.py)
"""

from pathlib import Path

from smolagents import CodeAgent

from gaia_agent.agent.answer import clean_answer
from gaia_agent.agent.instructions import INSTRUCTIONS
from gaia_agent.attachments import load_attachment
from gaia_agent.llm import MODEL_ID, build_model
from gaia_agent.scoring import download_file
from gaia_agent.tools import build_tools

FILES_DIR = Path("downloads")
MAX_STEPS = 12


class GaiaAgent:
    def __init__(self):
        self.agent = CodeAgent(
            tools=build_tools(),
            model=build_model(),
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
            path = download_file(task_id, file_name, FILES_DIR)
            attachment = load_attachment(path)
            task = f"{question}\n\n{attachment.text}"
            images = attachment.images or None

        answer = self.agent.run(task, images=images)
        return clean_answer(answer)
