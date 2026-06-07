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
based exclusively on student reviews provided to you. Treat these reviews as the complete and total universe of available information.

Rules you must follow:
1. Answer ONLY from the review excerpts in the context below. Do not use your general \
training knowledge about teaching, universities, or any topic.
2. If a user asks if "other" professors teach a class, or asks for a comparison, and the documents only show one professor fitting the criteria, DO NOT say you lack information. Instead, explicitly state that the documents only mention that one person. (For example: "Based on the provided reviews, Abdul Khan is the only professor listed who teaches CIS142. There is no information about other professors teaching it.")
3. If the context is completely unrelated to the prompt (e.g., asking about a subject not in the documents at all), ONLY THEN respond with exactly: "I don't have enough information in the provided reviews to answer that question."
4. At the end of every response, list the source files you actually drew from to generate \
the text, formatted as:
   Sources: [filename1.txt, filename2.txt]
5. When multiple reviews say different things, summarize the range of opinions fairly.\
"""


def ask(question: str, professor_filter: str | None = None, bm25_data: dict | None = None) -> dict:
    """
    Run the full RAG pipeline for a single question and return a structured result.

    Steps:
      1. Retrieve the top-5 most relevant review chunks from ChromaDB.
      2. Format each chunk as a labeled block so the LLM can reference sources by name.
      3. Send the formatted context + question to llama-3.3-70b-versatile via Groq.
      4. Return the LLM's response and the list of source filenames.

    Args:
      professor_filter: If provided, restricts retrieval to chunks from this professor only.
        Pass None (default) to search across all professors.
    """
    # Step 1: semantic retrieval — returns top-5 chunks ranked by cosine distance.
    # professor_filter is forwarded to ChromaDB's where clause if set.
    chunks = retrieve_context(question, collection, k=5, professor_filter=professor_filter, bm25_data=bm25_data)

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

def rewrite_query(message: str, history: list[dict]) -> str:
    """
    Uses the LLM to rewrite conversational follow-ups into standalone search queries.
    If the user says "What is his workload?", it rewrites it to "What is Abdul Khan's workload?"
    """
    if not history:
        return message # First turn, no history to resolve
        
    rewrite_prompt = """You are a search query reformulator. 
Given the chat history and the user's latest follow-up question, rewrite the follow-up question \
to be a standalone search query that contains all necessary names, classes, and subjects.
If the question is already standalone, return it exactly as is.
DO NOT answer the question. ONLY return the rewritten query text."""

    # Build a temporary message array just for the rewrite task
    messages = [{"role": "system", "content": rewrite_prompt}]
    
    # Safely unpack the history just like we do in the main chat function
    for turn in history:
        if "role" in turn and "content" in turn:
            messages.append({"role": turn["role"], "content": str(turn["content"])})
            
    messages.append({
        "role": "user", 
        "content": f"Rewrite this follow-up question to be a standalone query: {message}"
    })

    # Use a fast, deterministic call
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0 # Keep it strictly factual
    )
    
    return response.choices[0].message.content.strip()


def chat(
    message: str,
    history: list[dict],
    professor_filter: str | None = None,
    bm25_data: dict | None = None,
) -> str:
    
    # 1. REWRITE THE QUERY SO THE DATABASE KNOWS THE CONTEXT
    search_query = rewrite_query(message, history)
    
    # Optional debug print so you can see the magic happening in your terminal:
    print(f"\n[DEBUG] Original: {message} --> Rewritten: {search_query}")

    # 2. RUN RETRIEVAL USING THE REWRITTEN QUERY
    chunks = retrieve_context(
        search_query, # <-- Make sure you change this from `message` to `search_query`
        collection, 
        k=15, 
        professor_filter=professor_filter, 
        bm25_data=bm25_data
    )

    context_str = "\n\n---\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    # 3. Build the messages array (The rest stays exactly the same)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Scrub Gradio's history to explicitly drop the unsupported 'metadata' key
    for turn in history:
        if "role" in turn and "content" in turn:
            messages.append({
                "role": turn["role"],
                "content": str(turn["content"])
            })
            
    messages.append({
        "role": "user",
        "content": f"Context:\n{context_str}\n\nQuestion: {message}",
    })

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    return response.choices[0].message.content


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
