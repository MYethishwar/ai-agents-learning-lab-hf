"""
Gradio app for the Hugging Face Space, based on the course's Final_Assignment_Template.

Click the button -> fetch the 20 questions -> run GaiaAgent on each -> submit -> show the score.
"""

import os

import gradio as gr
import pandas as pd

from gaia_agent import scoring
from gaia_agent.agent import GaiaAgent


def run_and_submit_all(profile: gr.OAuthProfile | None):
    if not profile:
        return "Please log in to Hugging Face with the button.", None
    username = profile.username

    # Link to this Space's code, required by the API so others can verify the agent.
    space_id = os.getenv("SPACE_ID")
    agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"

    # 1. Create the agent
    try:
        agent = GaiaAgent()
    except Exception as error:
        return f"Error initializing agent: {error}", None

    # 2. Fetch the questions
    try:
        questions = scoring.get_questions()
    except Exception as error:
        return f"Error fetching questions: {error}", None

    # 3. Answer every question
    answers, log = [], []
    for item in questions:
        task_id, question = item["task_id"], item["question"]
        try:
            answer = agent(question, task_id, item.get("file_name", ""))
        except Exception as error:
            answer = f"AGENT ERROR: {error}"
        else:
            answers.append({"task_id": task_id, "submitted_answer": answer})
        log.append({"Task ID": task_id, "Question": question, "Submitted Answer": answer})

    if not answers:
        return "The agent did not produce any answers to submit.", pd.DataFrame(log)

    # 4. Submit
    try:
        result = scoring.submit(username, agent_code, answers)
    except Exception as error:
        return f"Submission failed: {error}", pd.DataFrame(log)

    status = (
        f"Submission successful!\n"
        f"User: {result.get('username')}\n"
        f"Overall score: {result.get('score', 'N/A')}% "
        f"({result.get('correct_count', '?')}/{result.get('total_attempted', '?')} correct)\n"
        f"Message: {result.get('message', '')}"
    )
    return status, pd.DataFrame(log)


with gr.Blocks() as demo:
    gr.Markdown("# GAIA Agent - Final Assignment")
    gr.Markdown(
        """
        1. Log in with your Hugging Face account.
        2. Click **Run Evaluation & Submit All Answers**. Answering all 20 questions takes several minutes.
        """
    )
    gr.LoginButton()
    run_button = gr.Button("Run Evaluation & Submit All Answers")
    status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
    results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)
    run_button.click(fn=run_and_submit_all, outputs=[status_output, results_table])
