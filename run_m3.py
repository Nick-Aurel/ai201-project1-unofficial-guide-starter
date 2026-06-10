#!/usr/bin/env python3
"""Run Milestone 3: ingest all sources, chunk, print stats and sample output."""

from ingest import ingest_all
from chunk import chunk_all_documents, print_sample_chunks, print_stats, save_chunks


def main() -> None:
    print("=== Milestone 3: Document Ingestion ===\n")
    ingest_all()

    print("\n=== Milestone 3: Chunking ===\n")
    chunks = chunk_all_documents()
    save_chunks(chunks)
    print_stats(chunks)
    print_sample_chunks(chunks, n=5)
    print("\nDone. Chunks saved to documents/chunks.json")


if __name__ == "__main__":
    main()
