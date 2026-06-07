import os
import pathlib
import gradio as gr
from query import ask

# Derive professor names from the documents directory so the list stays in sync
# automatically if a new professor file is ever added.
_docs_dir = pathlib.Path(__file__).parent / "documents"
_professors = ["All Professors"] + [
    f.removesuffix(".txt").replace("_", " ")
    for f in sorted(os.listdir(_docs_dir))
    if f.endswith(".txt")
]


def handle_query(question: str, professor_selection: str):
    # Convert the dropdown value to the filter format expected by ask().
    # "All Professors" means no filter; any other value is an exact professor name.
    professor_filter = None if professor_selection == "All Professors" else professor_selection
    result = ask(question, professor_filter=professor_filter)
    sources_str = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_str


with gr.Blocks(title="Wright College Professor Guide") as demo:
    gr.Markdown("# The Unofficial Wright College CS Professor Guide")
    gr.Markdown(
        "Ask questions about CS professors at Wright College based on Rate My Professors reviews."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about Professor Khan's teaching style?",
    )
    professor_dd = gr.Dropdown(
        choices=_professors,
        value="All Professors",
        label="Filter by Professor (optional)",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=[inp, professor_dd], outputs=[answer, sources])
    inp.submit(handle_query, inputs=[inp, professor_dd], outputs=[answer, sources])

demo.launch()
