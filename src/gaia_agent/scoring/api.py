"""
Thin client for the course's scoring API.

The API has four routes (see https://agents-course-unit4-scoring.hf.space/docs):
    GET  /questions        -> the 20 GAIA level-1 questions
    GET  /random-question  -> one random question (not used here)
    GET  /files/{task_id}  -> the file attached to a question, if any
    POST /submit           -> score a list of answers and update the leaderboard
"""

from pathlib import Path

import requests
from huggingface_hub import hf_hub_download

API_URL = "https://agents-course-unit4-scoring.hf.space"


def get_questions() -> list[dict]:
    """Return every question as a dict with keys: task_id, question, Level, file_name."""
    response = requests.get(f"{API_URL}/questions", timeout=30)
    response.raise_for_status()
    return response.json()


def download_file(task_id: str, file_name: str, folder: Path) -> Path:
    """Download the file attached to a question and return its local path.

    Files are cached on disk, so running the agent twice does not download twice.
    """
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / file_name
    if path.exists():
        return path

    response = requests.get(f"{API_URL}/files/{task_id}", timeout=60)
    if response.ok:
        path.write_bytes(response.content)
        return path

    # The course API sometimes answers 404 for every file. The same files are in the
    # official GAIA dataset, which is gated: accept its terms on the dataset page once,
    # and set HF_TOKEN to a token of that account.
    return Path(
        hf_hub_download(
            repo_id="gaia-benchmark/GAIA",
            repo_type="dataset",
            filename=f"2023/validation/{file_name}",
            local_dir=folder,
        )
    )


def submit(username: str, agent_code: str, answers: list[dict]) -> dict:
    """Send answers for scoring.

    username:   your Hugging Face username
    agent_code: public link to your Space code, e.g. https://huggingface.co/spaces/<user>/<space>/tree/main
    answers:    [{"task_id": "...", "submitted_answer": "..."}, ...]
    """
    payload = {"username": username.strip(), "agent_code": agent_code, "answers": answers}
    response = requests.post(f"{API_URL}/submit", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()
