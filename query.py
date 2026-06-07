"""
query.py — Milestone 5: Grounded Generation

Pipeline stage: user question → retrieve context → Groq LLM → grounded answer with citations

This module is the bridge between the vector store (embed.py) and the Gradio interface (app.py).
It enforces grounding by injecting retrieved review text directly into the prompt and
instructing the LLM never to draw on its general training knowledge.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from embed import load_collection, retrieve_context

load_dotenv()

# Load the pre-built vector store from disk. This must be built first by running embed.py.
# load_collection() opens the existing ChromaDB at ./chroma_db/ without re-embedding.
collection = load_collection()

# Initialize the Groq client once at module level so it is reused across calls.
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# The system prompt is the primary grounding mechanism.
# Rule 1 prohibits the model from using general training knowledge.
# Rule 2 provides an exact fallback string for out-of-scope questions.
# Rule 3 requires source citations in every response, making attribution visible in the output.
SYSTEM_PROMPT = """\
You are a helpful assistant answering questions about CS professors at Wright College \
based exclusively on student reviews provided to you.

Rules you must follow:
1. Answer ONLY from the review excerpts in the context below. Do not use your general \
training knowledge about teaching, universities, or any topic.
2. If the provided reviews do not contain enough information to answer the question, \
respond with exactly: "I don't have enough information in the provided reviews to answer that question."
3. At the end of every response, list the source files you drew from, formatted as:
   Sources: [filename1.txt, filename2.txt]
4. When multiple reviews say different things, summarize the range of opinions fairly.\
"""


def ask(question: str) -> dict:
    """
    Run the full RAG pipeline for a single question and return a structured result.

    Steps:
      1. Retrieve the top-5 most relevant review chunks from ChromaDB.
      2. Format each chunk as a labeled block so the LLM can reference sources by name.
      3. Send the formatted context + question to llama-3.3-70b-versatile via Groq.
      4. Return the LLM's response and the list of source filenames.
    """
    # Step 1: semantic retrieval — returns top-5 chunks ranked by cosine distance
    chunks = retrieve_context(question, collection, k=5)

    # Step 2: format context blocks with source labels.
    # Embedding each chunk's filename in the context lets the LLM cite sources accurately.
    context_blocks = [
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    ]
    context_str = "\n\n---\n\n".join(context_blocks)

    # Step 3: call the Groq API.
    # The system prompt enforces grounding; the user message carries the retrieved context.
    # Keeping context in the user message (not system) is intentional: it keeps the
    # grounding rules in system and the evidence in user, which mirrors how the model
    # was trained to process instruction-following tasks.
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context_str}\n\nQuestion: {question}",
            },
        ],
    )

    answer = response.choices[0].message.content

    # Deduplicate sources from the retrieval step (multiple chunks can share a source file).
    sources = sorted({c["source"] for c in chunks})

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    test_cases = [
        # In-scope query — should return a grounded answer with source citations
        "How does Professor Best connect his coursework to the real world and the tech industry?",
        # Out-of-scope query — should trigger the exact refusal string from rule 2
        "What is the capital of France?",
    ]

    for question in test_cases:
        print(f"\n{'=' * 70}")
        print(f"QUESTION: {question}")
        print("=" * 70)
        result = ask(question)
        print(result["answer"])
        print(f"\nSources (from retrieval): {result['sources']}")
