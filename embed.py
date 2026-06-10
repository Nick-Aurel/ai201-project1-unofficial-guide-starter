"""
Milestone 4 — Embed chunks and store in ChromaDB.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings.
"""

from __future__ import annotations

from functools import lru_cache

import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

from chunk import load_chunks
from config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )


def get_or_create_collection(client: chromadb.ClientAPI, reset: bool = False):
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except (ValueError, NotFoundError):
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_id(metadata: dict) -> str:
    return f"{metadata['source_filename']}::{metadata['chunk_index']}"


def _chroma_metadata(metadata: dict) -> dict:
    """ChromaDB metadata values must be scalar types."""
    chroma_meta = {
        "source_filename": metadata.get("source_filename", ""),
        "source_url": metadata.get("source_url", ""),
        "source_type": metadata.get("source_type", ""),
        "title": metadata.get("title", ""),
        "chunk_index": int(metadata.get("chunk_index", 0)),
    }
    course_code = metadata.get("course_code")
    if course_code:
        chroma_meta["course_code"] = course_code
    return chroma_meta


def embed_chunks(reset: bool = False, batch_size: int = 64) -> int:
    chunks = load_chunks()
    if not chunks:
        raise ValueError("No chunks to embed.")

    model = get_embedding_model()
    client = get_chroma_client()
    collection = get_or_create_collection(client, reset=reset)

    if not reset and collection.count() > 0:
        print(f"Collection already has {collection.count()} chunks. Use reset=True to rebuild.")
        return collection.count()

    texts = [chunk["text"] for chunk in chunks]
    ids = [_chunk_id(chunk["metadata"]) for chunk in chunks]
    metadatas = [_chroma_metadata(chunk["metadata"]) for chunk in chunks]

    print(f"Embedding {len(texts)} chunks with {EMBEDDING_MODEL}...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    add_batch = 100
    for start in range(0, len(texts), add_batch):
        end = start + add_batch
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end].tolist(),
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )

    count = collection.count()
    print(f"Stored {count} chunks in ChromaDB at {CHROMA_PATH}")
    return count


if __name__ == "__main__":
    embed_chunks(reset=True)
