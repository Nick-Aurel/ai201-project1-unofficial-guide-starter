"""
Milestone 4 — Semantic retrieval over ChromaDB.
"""

from __future__ import annotations

from typing import Any

from embed import get_chroma_client, get_embedding_model, get_or_create_collection
from config import TOP_K


def retrieve(query: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    """
    Return top-k chunks for a query.

    Each result dict contains:
      - text: chunk content
      - metadata: source_filename, source_url, source_type, title, chunk_index, ...
      - distance: cosine distance (lower = more similar; 0 = identical)
    """
    model = get_embedding_model()
    client = get_chroma_client()
    collection = get_or_create_collection(client, reset=False)

    if collection.count() == 0:
        raise RuntimeError("Vector store is empty. Run `python embed.py` first.")

    query_embedding = model.encode([query], convert_to_numpy=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": doc,
            "metadata": meta,
            "distance": float(dist),
        }
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]


def print_retrieval_results(query: str, results: list[dict[str, Any]]) -> None:
    print(f"\nQuery: {query}")
    print("-" * 72)
    for rank, item in enumerate(results, 1):
        meta = item["metadata"]
        source = meta.get("source_filename", "unknown")
        chunk_index = meta.get("chunk_index", "?")
        distance = item["distance"]
        preview = item["text"].replace("\n", " ")
        if len(preview) > 320:
            preview = preview[:320] + "..."
        print(f"\n#{rank}  distance={distance:.4f}  source={source} (chunk {chunk_index})")
        print(f"    {preview}")


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What are INFO affiliation GPA requirements?"
    results = retrieve(q)
    print_retrieval_results(q, results)
