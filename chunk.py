"""
Milestone 3 — Chunking pipeline.

Splits cleaned documents into chunks per planning.md:
  - 450 characters, 80 overlap (default recursive split)
  - Per-source rules for reviews, Reddit, wikis, and articles
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
SOURCES_PATH = ROOT / "sources.json"
CLEAN_DIR = ROOT / "documents" / "cleaned"
CHUNKS_PATH = ROOT / "documents" / "chunks.json"

CHUNK_SIZE = 450
CHUNK_OVERLAP = 80
MIN_CHUNK_LEN = 50
SHORT_DOC_MAX = CHUNK_SIZE


def load_sources() -> dict[str, dict[str, Any]]:
    with SOURCES_PATH.open(encoding="utf-8") as f:
        return {item["filename"]: item for item in json.load(f)}


def load_cleaned_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    sources = load_sources()

    for path in sorted(CLEAN_DIR.glob("*.txt")):
        meta = sources.get(path.name, {})
        documents.append(
            {
                "source_filename": path.name,
                "source_url": meta.get("source_url", ""),
                "source_type": meta.get("source_type", "unknown"),
                "title": meta.get("title", path.stem),
                "course_code": meta.get("course_code", ""),
                "text": path.read_text(encoding="utf-8"),
            }
        )
    return documents


def fixed_size_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if not text:
        return []

    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK_LEN:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def split_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return parts or [text]


def recursive_paragraph_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    for paragraph in split_paragraphs(text):
        if len(paragraph) <= CHUNK_SIZE:
            chunks.append(paragraph)
        else:
            chunks.extend(fixed_size_chunks(paragraph))
    return chunks


def split_on_headers(text: str) -> list[str]:
    sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]
    if not sections:
        return recursive_paragraph_chunks(text)

    chunks: list[str] = []
    for section in sections:
        if len(section) <= CHUNK_SIZE:
            chunks.append(section)
        else:
            chunks.extend(recursive_paragraph_chunks(section))
    return chunks


def split_reddit_comments(text: str) -> list[str]:
    blocks = re.split(r"\n---\n", text)
    blocks = [b.strip() for b in blocks if b.strip()]

    chunks: list[str] = []
    for block in blocks:
        if len(block) <= CHUNK_SIZE:
            chunks.append(block)
        else:
            chunks.extend(recursive_paragraph_chunks(block))
    return chunks


def split_reviews(text: str) -> list[str]:
    """Split professor/course reviews into one chunk per review when possible."""
    rmp_blocks = re.split(
        r"(?=INFO\d{4}\s*\n(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))",
        text,
    )
    rmp_blocks = [b.strip() for b in rmp_blocks if b.strip() and len(b.strip()) >= MIN_CHUNK_LEN]

    if len(rmp_blocks) > 1:
        chunks: list[str] = []
        for block in rmp_blocks:
            if len(block) <= SHORT_DOC_MAX:
                chunks.append(block)
            else:
                chunks.extend(fixed_size_chunks(block))
        return chunks

    coursicle_blocks = re.split(r"(?=Review \d+ —)", text)
    coursicle_blocks = [b.strip() for b in coursicle_blocks if b.strip() and len(b.strip()) >= MIN_CHUNK_LEN]
    if len(coursicle_blocks) > 1:
        return coursicle_blocks

    blocks = split_paragraphs(text)
    chunks = []
    for block in blocks:
        if len(block) <= SHORT_DOC_MAX:
            chunks.append(block)
        else:
            chunks.extend(fixed_size_chunks(block))
    return chunks


def strip_metadata_header(text: str) -> str:
    """Remove the ingestion header while keeping course/source context in chunks."""
    lines = text.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("SOURCE:") or line.startswith("URL:") or line.startswith("TYPE:") or line.startswith("COURSE:"):
            body_start = i + 1
        elif line.strip() == "" and body_start > 0:
            body_start = i + 1
            break
    return "\n".join(lines[body_start:]).strip()


def chunk_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    source_type = doc["source_type"]
    raw_text = doc["text"]
    header_lines = []
    for line in raw_text.splitlines():
        if line.startswith(("SOURCE:", "URL:", "TYPE:", "COURSE:")):
            header_lines.append(line)
        else:
            break
    header = "\n".join(header_lines)

    text = strip_metadata_header(raw_text)

    if source_type in {"professor_reviews", "course_review_site"}:
        pieces = split_reviews(text)
    elif source_type == "reddit":
        pieces = split_reddit_comments(text)
    elif source_type in {"student_wiki", "official_department", "official_outcomes", "campus_news"}:
        pieces = split_on_headers(text)
    else:
        pieces = recursive_paragraph_chunks(text)

    chunks: list[dict[str, Any]] = []
    for idx, piece in enumerate(pieces):
        piece = piece.strip()
        if len(piece) < MIN_CHUNK_LEN:
            continue

        chunk_text = piece
        if header:
            chunk_text = f"{header}\n\n{piece}"

        metadata = {
            "source_filename": doc["source_filename"],
            "source_url": doc["source_url"],
            "source_type": doc["source_type"],
            "title": doc["title"],
            "chunk_index": idx,
        }
        if doc.get("course_code"):
            metadata["course_code"] = doc["course_code"]

        chunks.append({"text": chunk_text, "metadata": metadata})

    return chunks


def chunk_all_documents() -> list[dict[str, Any]]:
    all_chunks: list[dict[str, Any]] = []
    for doc in load_cleaned_documents():
        all_chunks.extend(chunk_document(doc))
    return all_chunks


def save_chunks(chunks: list[dict[str, Any]]) -> Path:
    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_PATH.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    return CHUNKS_PATH


def print_sample_chunks(chunks: list[dict[str, Any]], n: int = 5) -> None:
    print(f"\n{'=' * 72}")
    print(f"SAMPLE CHUNKS ({n} random)")
    print("=" * 72)

    sample = random.sample(chunks, min(n, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        meta = chunk["metadata"]
        print(f"\n--- Chunk {i} ---")
        print(f"Source: {meta['source_filename']} (index {meta['chunk_index']}, type={meta['source_type']})")
        preview = chunk["text"]
        if len(preview) > 500:
            preview = preview[:500] + "..."
        print(preview)


def print_stats(chunks: list[dict[str, Any]]) -> None:
    by_source: dict[str, int] = {}
    for chunk in chunks:
        name = chunk["metadata"]["source_filename"]
        by_source[name] = by_source.get(name, 0) + 1

    print(f"\nTotal chunks: {len(chunks)}")
    print("Chunks per document:")
    for name, count in sorted(by_source.items()):
        print(f"  {name}: {count}")


if __name__ == "__main__":
    random.seed(42)
    chunks = chunk_all_documents()
    save_chunks(chunks)
    print_stats(chunks)
    print_sample_chunks(chunks)
    print(f"\nSaved chunks to {CHUNKS_PATH}")
