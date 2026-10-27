---
title: GAIA Agent Final Assignment
emoji: 🕵🏻‍♂️
colorFrom: indigo
colorTo: indigo
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_expiration_minutes: 480
---

# GAIA Agent: Hugging Face Agents Course, Unit 4

An agent built with **smolagents** that answers the 20 GAIA level-1 questions from the course's final assignment.
The goal is **30% or more** (6 of 20) under an exact-match check.

## Architecture

```
app.py / run_local.py         entry points: Space UI, or local runs with cached answers
        │
        ▼
scoring_api.py                get questions, download attachments, submit answers
        │
        ▼
agent.py  GaiaAgent           one call per question
   ├─ attachments.py          open the attached file first (image / audio / code / spreadsheet)
   ├─ CodeAgent (smolagents)  think → write Python → call tools → repeat → final_answer
   │     ├─ llm.py            the model: Gemini (free tier) through its OpenAI-compatible API
   │     └─ tools.py          web_search, visit_webpage, youtube_transcript
   └─ clean_answer()          strip "FINAL ANSWER:", quotes, trailing period; lists → "a, b, c"
```

| File | What it does |
|---|---|
| [llm.py](llm.py) | Which model to use (default `gemini-2.5-flash`), the Gemini endpoint, and the requests-per-minute cap |
| [agent.py](agent.py) | Builds the `CodeAgent` with the GAIA answer rules, runs one question, cleans the answer |
| [tools.py](tools.py) | The 3 tools the agent can call |
| [attachments.py](attachments.py) | Turns an attached file into prompt text or an image |
| [scoring_api.py](scoring_api.py) | The course API: `/questions`, `/files/{task_id}`, `/submit` |
| [app.py](app.py) | Gradio app for the Space (log in, run, submit), based on the course template |
| [run_local.py](run_local.py) | Run chosen questions locally, keep answers in `answers.json`, submit when ready |

## Why these tools and nothing more

Each of the 20 questions was read to see what it needs:

| Need | Questions | How it is handled |
|---|---|---|
| Find facts on the web | Mercedes Sosa, dinosaur FA, Polish Raymond actor, 1977 Yankees, Universe Today paper, Nedoshivina specimens, 1928 Olympics, Taishō Tamai, Malko Competition, LibreTexts vet | `web_search` (built into smolagents) + `visit_webpage` (ours, sends a User-Agent so Wikipedia allows it) |
| What is said in a YouTube video | Teal'c | `youtube_transcript` tool |
| Logic, puzzles, small calculations | reversed text, commutativity table, botanical vegetables | No tool: the model reasons, or writes Python (CodeAgent runs it) |
| Image | chess position | Sent to the model as an image (needs a vision model) |
| Audio | pie recipe, homework pages | Transcribed by Gemini before the agent starts |
| Python file | final numeric output | Code added to the prompt; the agent can run its logic |
| Excel file | food sales | Table added to the prompt; the agent can load it with pandas |

Not handled: the bird-species video. Counting birds on screen needs the video frames, and a transcript can't give that.

## Setup

### Secrets / environment variables

Both are free.

| Name | Needed for |
|---|---|
| `GEMINI_API_KEY` | The LLM and audio transcription. Free key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `HF_TOKEN` | Only for downloading attachments from the GAIA dataset (free). A read token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `MODEL_ID` | Optional. Default is `gemini-2.5-flash`. Must be a model that accepts images and audio |

The Gemini free tier allows only a few requests per minute, so the agent caps itself at 8 per minute (see [llm.py](llm.py)).
A full run of all 20 questions therefore takes a while. Test a few with `run_local.py --only ...` first.

**Attachments:** the course API currently returns 404 for every file. The code then downloads the same file
from the gated [gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) dataset.
Open that page once while logged in and accept its terms, so your `HF_TOKEN` can read it.

### Run locally

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
export GEMINI_API_KEY=<your key>                   # PowerShell: $env:GEMINI_API_KEY="<your key>"
.venv/Scripts/hf auth login                        # stores HF_TOKEN for the GAIA files
.venv/Scripts/python run_local.py --list           # numbered questions
.venv/Scripts/python run_local.py --only 3 6 9     # try a few
.venv/Scripts/python run_local.py                  # everything not answered yet
.venv/Scripts/python run_local.py --submit --username <hf-user> --space <hf-user>/<space-name>
```

### Deploy to a Hugging Face Space

1. Create a **public** Gradio Space and push these files to it. This README's header configures the Space.
2. In the Space settings, add `GEMINI_API_KEY` and `HF_TOKEN` as secrets.
3. Open the Space, log in, and click **Run Evaluation & Submit All Answers**.
4. If you scored 30% or more, claim the certificate at
   [agents-course/Unit4-Final-Certificate](https://huggingface.co/spaces/agents-course/Unit4-Final-Certificate).
