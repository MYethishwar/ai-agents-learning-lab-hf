"""
The LLM used by the agent and for audio transcription: Google Gemini, free tier.

Gemini offers an OpenAI-compatible API, so we talk to it with the standard `openai` client.
Get a free key at https://aistudio.google.com/apikey and set it as GEMINI_API_KEY.
"""

import os

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Free-tier model that understands text, images (chess question) and audio (mp3 questions).
# To try another one, set MODEL_ID. Free models: https://ai.google.dev/gemini-api/docs/pricing
MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

# The free tier allows only a few requests per minute. Stay under it so runs don't fail.
# Your exact limits: https://aistudio.google.com/rate-limit
REQUESTS_PER_MINUTE = 8
