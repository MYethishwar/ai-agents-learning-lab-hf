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
ui/app.py  or  cli/run_local.py   entry points: Space UI, or local runs with cached answers
        │
        ▼
scoring/                          get questions, download attachments, submit answers
        │
        ▼
agent/  GaiaAgent                 one call per question
   ├─ attachments/                open the attached file first (image / audio / code / spreadsheet)
   ├─ CodeAgent (smolagents)      think → write Python → call tools → repeat → final_answer
   │     ├─ llm/                  the model: Gemini (free tier) through its OpenAI-compatible API
   │     └─ tools/                web_search, visit_webpage, youtube_transcript
   └─ answer.clean_answer()       strip "FINAL ANSWER:", quotes, trailing period; lists → "a, b, c"
```

### Project layout

One folder per service, all inside `src/gaia_agent/`:

```
app.py                       Space entry point: adds src/ to the path and launches ui/app.py
pyproject.toml               the package and its `gaia-agent` command
requirements.txt             dependencies the Space installs (same list as pyproject.toml)
src/gaia_agent/
├── agent/
│   ├── gaia_agent.py        GaiaAgent: builds the CodeAgent, runs one question
│   ├── instructions.py      GAIA answer rules added to the system prompt
│   └── answer.py            clean_answer(): makes the answer safe for exact match
├── llm/
│   └── gemini.py            model id, endpoint, rate cap; build_model() and chat_client()
├── tools/
│   ├── __init__.py          build_tools(): the 3 tools, and why each one is needed
│   ├── web_page.py          visit_webpage (sends a User-Agent so Wikipedia allows it)
│   └── youtube.py           youtube_transcript
├── attachments/
│   ├── loader.py            turns an attached file into prompt text or an image
│   └── audio.py             mp3 → transcript with Gemini
├── scoring/
│   └── api.py               the course API: /questions, /files/{task_id}, /submit
├── ui/
│   └── app.py               Gradio app (log in, run, submit), based on the course template
└── cli/
    └── run_local.py         run chosen questions, cache them in answers.json, submit when ready
```

Each folder's `__init__.py` exports what the other services use, e.g. `from gaia_agent.llm import build_model`.

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

The Gemini free tier allows only a few requests per minute, so the agent caps itself at 8 per minute (see [gemini.py](src/gaia_agent/llm/gemini.py)).
The free tier also allows only about 20 requests **per day per model**, and one question takes 2–12 requests.
Each model has its own daily quota, so you can spread questions over several models with `MODEL_ID`.

**Attachments:** the course API currently returns 404 for every file. The code then downloads the same file
from the gated [gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) dataset.
Open that page once while logged in and accept its terms. If your token is fine-grained, also tick
"Read access to contents of all public gated repos you can access" on it.

### Run locally

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e .   # installs the package and the `gaia-agent` command
export GEMINI_API_KEY=<your key>                         # PowerShell: $env:GEMINI_API_KEY="<your key>"
.venv/Scripts/hf auth login                              # stores HF_TOKEN for the GAIA files
.venv/Scripts/gaia-agent --list                          # numbered questions, [x] = answered
.venv/Scripts/gaia-agent --only 3 6 9                    # try a few
MODEL_ID=gemini-2.5-flash-lite .venv/Scripts/gaia-agent --only 12   # same, on another model's quota
.venv/Scripts/gaia-agent                                 # everything not answered yet
.venv/Scripts/gaia-agent --submit --username <hf-user> --space <hf-user>/<space-name>
```

Answers are saved in `answers.json` after each question. Two runs on different models can work at the same time.

### Deploy to a Hugging Face Space

Gradio Spaces on free CPU now need a PRO subscription. Two options:

- **Free (what this project uses):** a public **static** Space that only holds the code, as the `agent_code`
  link for the course. Run the agent locally and submit with `gaia-agent --submit`. The score goes to the same
  leaderboard as the Space button.
- **PRO:** a public Gradio Space with this repo as is (`app.py` is the entry point). Add `GEMINI_API_KEY` and
  `HF_TOKEN` as secrets, open the Space, log in, and click **Run Evaluation & Submit All Answers**.
  A full run needs more than the free Gemini quota allows in a day.

If you scored 30% or more, claim the certificate at
   [agents-course/Unit4-Final-Certificate](https://huggingface.co/spaces/agents-course/Unit4-Final-Certificate).
