"""
Milestone 5 — Gradio query interface for The Unofficial Guide.

Run: python app.py
Open: http://localhost:7860
"""

from __future__ import annotations

import gradio as gr

from query import ask


def handle_query(question: str) -> tuple[str, str]:
    result = ask(question)
    sources = "\n".join(f"• {source}" for source in result["sources"])
    return result["answer"], sources


demo = gr.Blocks(title="The Unofficial Guide — Cornell INFO")
with demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask questions about Cornell's **Information Science** major — courses, professors, "
        "affiliation, enrollment, and careers. Answers are grounded in collected student and "
        "campus sources with citations."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g., What do students say about enrolling in core INFO classes?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
