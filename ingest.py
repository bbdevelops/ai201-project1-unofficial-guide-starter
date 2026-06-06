import os


def load_and_chunk_documents(docs_dir: str) -> list[dict]:
    chunks = []
    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith('.txt'):
            continue
        professor = filename.removesuffix('.txt').replace('_', ' ')
        with open(os.path.join(docs_dir, filename), encoding='utf-8') as f:
            content = f.read()
        for segment in content.split('\n\n'):
            segment = segment.strip()
            if segment:
                chunks.append({
                    "text": f"Professor: {professor}\n{segment}",
                    "source": filename,
                    "professor": professor,
                })
    return chunks


if __name__ == "__main__":
    import pathlib
    docs_dir = pathlib.Path(__file__).parent / "documents"
    chunks = load_and_chunk_documents(str(docs_dir))
    print(f"Total chunks: {len(chunks)}")
    print("\n--- chunks[0] ---")
    print(chunks[0])
    print("\n--- chunks[1] ---")
    print(chunks[1])
