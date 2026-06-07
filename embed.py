"""
embed.py — Milestone 4: Embedding and Retrieval

Pipeline stage: chunks (from ingest.py) → embeddings → ChromaDB vector store → semantic retrieval

This module handles two phases:
  1. BUILD: encode every chunk with all-MiniLM-L6-v2 and persist them in ChromaDB
  2. QUERY: encode a user query with the same model and return the top-k most similar chunks
"""

import pathlib
import chromadb
from rank_bm25 import BM25Okapi
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


def build_bm25_index(collection: chromadb.Collection) -> dict:
    """
    Fetch all documents from a ChromaDB collection and build an in-memory BM25 index.

    The corpus is derived directly from collection.get() so the BM25 vocabulary
    is guaranteed to match the vector store exactly — same chunks, same metadata.
    Returns a dict that retrieve_context() accepts as bm25_data.
    """
    result = collection.get()
    docs = result["documents"]
    metadatas = result["metadatas"]
    tokenized = [doc.lower().split() for doc in docs]
    return {
        "index": BM25Okapi(tokenized),
        "tokenized": tokenized,
        "docs": docs,
        "metadatas": metadatas,
    }


def retrieve_context(
    query: str,
    collection: chromadb.Collection,
    k: int = 5,
    professor_filter: str | None = None,
    bm25_data: dict | None = None,
) -> list[dict]:
    """
    Return the top-k chunks most relevant to the query.

    When bm25_data is None: pure semantic search (original behavior, backward-compatible).
    When bm25_data is provided: hybrid search — semantic + BM25 merged with RRF.

    Args:
      professor_filter: Restrict search to one professor's chunks. Applied to both the
        ChromaDB where-clause and the BM25 corpus filter so both paths stay in sync.
      bm25_data: Dict returned by build_bm25_index(). When provided, activates the
        hybrid path. Pass None to use pure semantic search.
    """
    where = {"professor": professor_filter} if professor_filter else None

    if bm25_data is None:
        # ── Pure semantic (original path) ─────────────────────────────────────
        query_embedding = model.encode([query]).tolist()
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

    # ── Hybrid path: semantic + BM25 → RRF ───────────────────────────────────
    n_candidates = max(k * 4, 20)

    # 1. Semantic candidates
    query_embedding = model.encode([query]).tolist()
    sem_results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_candidates,
        where=where,
    )
    semantic_hits = []
    for i in range(len(sem_results["documents"][0])):
        semantic_hits.append({
            "text": sem_results["documents"][0][i],
            "source": sem_results["metadatas"][0][i]["source"],
            "professor": sem_results["metadatas"][0][i]["professor"],
            "distance": sem_results["distances"][0][i],
        })

    # 2. BM25 candidates — filter corpus by professor if requested
    if professor_filter:
        indices = [
            i for i, m in enumerate(bm25_data["metadatas"])
            if m["professor"] == professor_filter
        ]
        if not indices:
            bm25_hits = []
        else:
            filtered_tokenized = [bm25_data["tokenized"][i] for i in indices]
            filtered_docs = [bm25_data["docs"][i] for i in indices]
            filtered_meta = [bm25_data["metadatas"][i] for i in indices]
            local_index = BM25Okapi(filtered_tokenized)
            scores = local_index.get_scores(query.lower().split())
            top_local = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_candidates]
            bm25_hits = [
                {
                    "text": filtered_docs[i],
                    "source": filtered_meta[i]["source"],
                    "professor": filtered_meta[i]["professor"],
                    "distance": 0.0,
                }
                for i in top_local
                if scores[i] > 0
            ]
    else:
        scores = bm25_data["index"].get_scores(query.lower().split())
        top_global = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n_candidates]
        bm25_hits = [
            {
                "text": bm25_data["docs"][i],
                "source": bm25_data["metadatas"][i]["source"],
                "professor": bm25_data["metadatas"][i]["professor"],
                "distance": 0.0,
            }
            for i in top_global
            if scores[i] > 0
        ]

    # 3. Reciprocal Rank Fusion
    rrf_scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, hit in enumerate(semantic_hits, start=1):
        key = hit["text"]
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (60 + rank)
        doc_map[key] = hit

    for rank, hit in enumerate(bm25_hits, start=1):
        key = hit["text"]
        rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (60 + rank)
        doc_map.setdefault(key, hit)

    ranked_keys = sorted(rrf_scores, key=lambda k: rrf_scores[k], reverse=True)
    return [doc_map[key] for key in ranked_keys[:k]]


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
