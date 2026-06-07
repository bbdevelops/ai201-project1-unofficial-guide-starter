"""
embed.py — Milestone 4: Embedding and Retrieval

Pipeline stage: chunks (from ingest.py) → embeddings → ChromaDB vector store → semantic retrieval

This module handles two phases:
  1. BUILD: encode every chunk with all-MiniLM-L6-v2 and persist them in ChromaDB
  2. QUERY: encode a user query with the same model and return the top-k most similar chunks
"""

import pathlib
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_and_chunk_documents

# Load the embedding model once at import time.
# all-MiniLM-L6-v2 is a lightweight, 384-dimension model trained on sentence pairs.
# It maps variable-length text to fixed-size vectors so cosine distance can measure
# semantic similarity between a query and any stored chunk.
model = SentenceTransformer("all-MiniLM-L6-v2")

_DB_PATH = str(pathlib.Path(__file__).parent / "chroma_db")
_COLLECTION = "professor_reviews"


def build_vector_store(
    chunks: list[dict],
    db_path: str = _DB_PATH,
    collection_name: str = _COLLECTION,
) -> chromadb.Collection:
    """
    Embed all chunks and write them to a persistent ChromaDB collection.

    ChromaDB stores both the raw document text and the embedding vector for each chunk.
    Using a PersistentClient means the vectors are saved to disk, so app.py can load
    them later without re-running the embedding step.
    """
    client = chromadb.PersistentClient(path=db_path)

    # Delete any existing collection first to avoid adding duplicate vectors
    # if this function is called more than once on the same database path.
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    # cosine distance: score 0 means vectors are identical, 2 means opposite.
    # Lower distance = more semantically similar to the query.
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [chunk["text"] for chunk in chunks]

    # Batch-encode all chunk texts. The model converts each string into a
    # 384-dimensional float vector capturing its semantic meaning.
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"source": c["source"], "professor": c["professor"]} for c in chunks
        ],
    )

    return collection


def load_collection(
    db_path: str = _DB_PATH,
    collection_name: str = _COLLECTION,
) -> chromadb.Collection:
    """
    Load an already-built ChromaDB collection from disk.

    Call this in app.py instead of build_vector_store so the app does not
    re-embed every time it starts.
    """
    client = chromadb.PersistentClient(path=db_path)
    return client.get_collection(name=collection_name)


def retrieve_context(
    query: str,
    collection: chromadb.Collection,
    k: int = 5,
    professor_filter: str | None = None,
) -> list[dict]:
    """
    Return the top-k chunks most semantically similar to the query.

    Process:
      1. Encode the query with the same model used during ingestion — this maps
         the query into the same 384-dimensional embedding space as the stored chunks.
      2. ChromaDB uses HNSW (approximate nearest-neighbor search) with cosine distance
         to find the k closest vectors to the query embedding.
      3. Return the matching documents along with their metadata and distance scores.

    Args:
      professor_filter: If provided, restrict the search to chunks whose 'professor'
        metadata field exactly matches this string (e.g. "Abdul Khan"). Pass None to
        search across all professors.
    """
    query_embedding = model.encode([query]).tolist()

    # Build the metadata filter only when a specific professor is requested.
    # ChromaDB's simple {"key": "value"} format performs exact string equality.
    where = {"professor": professor_filter} if professor_filter else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        where=where,
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "professor": results["metadatas"][0][i]["professor"],
            "distance": results["distances"][0][i],
        })
    return retrieved


if __name__ == "__main__":
    # ── Build ────────────────────────────────────────────────────────────────
    docs_dir = pathlib.Path(__file__).parent / "documents"
    chunks = load_and_chunk_documents(str(docs_dir))
    print(f"Loaded {len(chunks)} chunks. Building vector store...")
    collection = build_vector_store(chunks)
    print(f"Vector store built with {collection.count()} entries.\n")

    # ── Retrieval tests (3 of 5 evaluation-plan queries) ─────────────────────
    # These are chosen because they target specific, verifiable content in the
    # source documents, making it easy to judge whether retrieval is working.
    test_queries = [
        "How does Professor Best connect his coursework to the real world and the tech industry?",
        "What should a student expect regarding the workload, homework, and exams in Professor Khan's classes?",
        "What do students say about the textbook used in Professor Haji's class?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 70}")
        print(f"QUERY: {query}")
        print("=" * 70)
        results = retrieve_context(query, collection, k=5)
        for rank, r in enumerate(results, start=1):
            print(f"\n[Rank {rank}] Source: {r['source']}  Distance: {r['distance']:.4f}")
            print(r["text"])
