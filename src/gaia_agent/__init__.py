"""
GAIA agent for the Hugging Face Agents Course, Unit 4.

One folder per service (see README.md for the full picture):

    agent/        GaiaAgent: runs one question from start to final answer
    llm/          the model (Gemini, free tier) and its settings
    tools/        what the agent can call: web search, web pages, YouTube transcripts
    attachments/  opens a question's attached file (image, audio, code, spreadsheet)
    scoring/      the course API: questions, files, submit
    ui/           Gradio app for the Hugging Face Space
    cli/          local runner that caches answers and submits them
"""
