"""
compare_chunking.py — Stretch Goal: Chunking Strategy Comparison

Builds a second ChromaDB collection ("naive_reviews") using a fixed 200-character
sliding-window split, then runs the same 3 evaluation queries against both
collections so the results can be compared side-by-side.

Usage:
    python compare_chunking.py

The original "professor_reviews" collection must already exist on disk (run
embed.py first if it does not). This script will build "naive_reviews" from
scratch on every run before executing the comparison.
"""

import os
import pathlib
import textwrap

from embed import build_vector_store, load_collection, retrieve_context


DOCS_DIR = str(pathlib.Path(__file__).parent / "documents")
NAIVE_COLLECTION = "naive_reviews"
TOP_K = 3
CHUNK_SIZE = 200
OVERLAP = 20
STEP = CHUNK_SIZE - OVERLAP  # 180


def load_and_chunk_naive(
    docs_dir: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = OVERLAP,
) -> list[dict]:
    """
    Load documents and split them with a fixed-size sliding window.

    This deliberately ignores paragraph boundaries to show how blind character
    splits damage semantic coherence: individual reviews get sliced mid-sentence,
    and adjacent chunks may span text from two completely different reviews.
    """
    step = chunk_size - overlap
    chunks = []
    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(".txt"):
            continue
        professor = filename.removesuffix(".txt").replace("_", " ")
        with open(os.path.join(docs_dir, filename), encoding="utf-8") as f:
            content = f.read()
        i = 0
        while i < len(content):
            segment = content[i : i + chunk_size]
            if segment.strip():
                chunks.append(
                    {
                        "text": f"Professor: {professor}\n{segment}",
                        "source": filename,
                        "professor": professor,
                    }
                )
            i += step
    return chunks


def _print_result(rank: int, result: dict, width: int = 90) -> None:
    print(f"  [Rank {rank}] Source: {result['source']}  Distance: {result['distance']:.4f}")
    wrapped = textwrap.fill(result["text"], width=width, initial_indent="    ", subsequent_indent="    ")
    print(wrapped)
    print()


def compare_strategies(queries: list[str], k: int = TOP_K) -> None:
    original_col = load_collection()
    naive_col = load_collection(collection_name=NAIVE_COLLECTION)

    for query in queries:
        banner = "=" * 90
        print(f"\n{banner}")
        print(f"QUERY: {query}")
        print(banner)

        original_results = retrieve_context(query, original_col, k=k)
        naive_results = retrieve_context(query, naive_col, k=k)

        print(f"\n{'-' * 40}  ORIGINAL (paragraph split)  {'-' * 40}\n")
        for rank, r in enumerate(original_results, start=1):
            _print_result(rank, r)

        print(f"\n{'-' * 40}  NAIVE (200-char fixed split) {'-' * 40}\n")
        for rank, r in enumerate(naive_results, start=1):
            _print_result(rank, r)


if __name__ == "__main__":
    print("Building naive collection from fixed-character chunks...")
    naive_chunks = load_and_chunk_naive(DOCS_DIR)
    print(f"  Naive chunks: {len(naive_chunks)}")
    build_vector_store(naive_chunks, collection_name=NAIVE_COLLECTION)
    print(f"  Collection '{NAIVE_COLLECTION}' written to disk.\n")

    test_queries = [
        "What do students say about the textbook used in Professor Haji's class?",
        "How does Professor Best connect his coursework to the real world and the tech industry?",
        "What should a student expect regarding the workload, homework, and exams in Professor Khan's classes?",
    ]

    compare_strategies(test_queries)
