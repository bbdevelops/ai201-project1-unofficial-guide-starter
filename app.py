import os
import pathlib
import gradio as gr
from query import chat

# Derive professor names from the documents directory so the list stays in sync
# automatically if a new professor file is ever added.
_docs_dir = pathlib.Path(__file__).parent / "documents"
_professors = ["All Professors"] + [
    f.removesuffix(".txt").replace("_", " ")
    for f in sorted(os.listdir(_docs_dir))
    if f.endswith(".txt")
]


def handle_chat(message: str, history: list, professor_selection: str) -> str:
    professor_filter = None if professor_selection == "All Professors" else professor_selection
    return chat(message, history, professor_filter=professor_filter)


professor_dd = gr.Dropdown(
    choices=_professors,
    value="All Professors",
    label="Filter by Professor (optional)",
)

demo = gr.ChatInterface(
    fn=handle_chat,
    additional_inputs=[professor_dd],
    title="The Unofficial Wright College CS Professor Guide",
    description="Ask questions about CS professors at Wright College based on Rate My Professors reviews.",
)

demo.launch()
