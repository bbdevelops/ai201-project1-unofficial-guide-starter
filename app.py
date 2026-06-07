import gradio as gr
from query import ask


def handle_query(question: str):
    result = ask(question)
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
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
