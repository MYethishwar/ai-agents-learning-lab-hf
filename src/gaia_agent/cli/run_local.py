"""
Run the agent on your own machine, one question at a time, and keep the answers in answers.json.

Why: running all 20 questions inside the Space is slow and starts over on any error.
Here you can test a few questions, fix the agent, and only re-run what you need.

Examples:
    gaia-agent --list                      # show the questions with their numbers
    gaia-agent --only 3 12                 # answer questions 3 and 12
    gaia-agent                             # answer every question not answered yet
    gaia-agent --only 3 --force            # answer question 3 again
    gaia-agent --submit --username <you> --space <you>/<space-name>
"""

import argparse
import json
import sys
from pathlib import Path

from gaia_agent import scoring

ANSWERS_FILE = Path("answers.json")


def load_answers() -> dict:
    return json.loads(ANSWERS_FILE.read_text(encoding="utf-8")) if ANSWERS_FILE.exists() else {}


def save_answer(task_id: str, answer: str) -> None:
    # Re-read the file first, so two runs at once (e.g. on different models) don't overwrite each other.
    answers = load_answers()
    answers[task_id] = answer
    ANSWERS_FILE.write_text(json.dumps(answers, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # questions contain non-ASCII names; Windows consoles default to cp1252

    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="print the questions and exit")
    parser.add_argument("--only", type=int, nargs="*", help="question numbers to run (1-20)")
    parser.add_argument("--force", action="store_true", help="re-run questions that already have an answer")
    parser.add_argument("--submit", action="store_true", help="submit the answers in answers.json")
    parser.add_argument("--username", help="your Hugging Face username (for --submit)")
    parser.add_argument("--space", help="your Space id, e.g. user/space-name (for --submit)")
    args = parser.parse_args()

    questions = scoring.get_questions()
    answers = load_answers()

    if args.list:
        for number, item in enumerate(questions, start=1):
            file_note = f"  [file: {item['file_name']}]" if item.get("file_name") else ""
            done = "x" if item["task_id"] in answers else " "
            print(f"[{done}] {number:2}. {item['question'][:100]!r}{file_note}")
        return

    if args.submit:
        payload = [{"task_id": task_id, "submitted_answer": answer} for task_id, answer in answers.items()]
        agent_code = f"https://huggingface.co/spaces/{args.space}/tree/main"
        print(scoring.submit(args.username, agent_code, payload))
        return

    from gaia_agent.agent import GaiaAgent  # imported here so --list and --submit work without model keys

    agent = GaiaAgent()
    selected = args.only or range(1, len(questions) + 1)

    for number in selected:
        item = questions[number - 1]
        if item["task_id"] in answers and not args.force:
            continue
        print(f"\n===== Question {number}: {item['question'][:120]}")
        try:
            answer = agent(item["question"], item["task_id"], item.get("file_name", ""))
        except Exception as error:
            print(f"AGENT ERROR: {error}")
            continue
        answers[item["task_id"]] = answer
        save_answer(item["task_id"], answer)  # save after each question, so nothing is lost if a later one fails
        print(f"===== Answer {number}: {answer!r}")

    print(f"\n{len(answers)}/{len(questions)} questions answered. Saved in {ANSWERS_FILE}")


if __name__ == "__main__":
    main()
