"""
Entry point for the Hugging Face Space (Spaces run `python app.py` from the repo root).

The code lives in src/gaia_agent. Spaces install requirements.txt but not this project
itself, so add src/ to the import path here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from gaia_agent.ui.app import demo  # noqa: E402  (import after the path fix)

if __name__ == "__main__":
    demo.launch(debug=True, share=False)
