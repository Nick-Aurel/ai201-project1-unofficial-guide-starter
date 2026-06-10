"""
Milestone 5 — Grounded answer generation with Groq.

Retrieves relevant chunks, builds a grounded prompt, and returns an answer
with programmatic source attribution.
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_MODEL, REFUSAL_PHRASE, SOURCE_TYPE_LABELS
from retrieve import retrieve

load_dotenv()

SYSTEM_PROMPT = f"""You are The Unofficial Guide for Cornell Information Science.

Rules (follow strictly):
1. Answer ONLY using facts stated in the provided document excerpts.
2. Do NOT use general knowledge, assumptions, or information not present in the excerpts.
3. If the excerpts do not contain enough information to answer the question, respond with exactly:
   "{REFUSAL_PHRASE}"
4. Be concise and specific. Mention course codes, numbers, or professor names only when they appear in the excerpts.
5. Do not invent sources or statistics."""


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add your key from console.groq.com"
        )
    return Groq(api_key=api_key)


def _source_label(metadata: dict[str, Any]) -> str:
    source_type = metadata.get("source_type", "")
    return SOURCE_TYPE_LABELS.get(source_type, "Document")


def build_context(chunks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        filename = meta.get("source_filename", "unknown")
        label = _source_label(meta)
        parts.append(f"[Document {i}: {filename} ({label})]\n{chunk['text']}")
    return "\n\n".join(parts)


def _unique_sources(chunks: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for chunk in chunks:
        filename = chunk["metadata"].get("source_filename", "")
        if filename and filename not in seen:
            seen.add(filename)
            ordered.append(filename)
    return ordered


def ask(question: str, top_k: int | None = None) -> dict[str, Any]:
    """
    End-to-end RAG query.

    Returns:
        answer: grounded LLM response
        sources: unique source filenames (programmatic, from retrieval)
        chunks: retrieved chunk dicts with metadata and distances
    """
    if not question.strip():
        return {"answer": "Please enter a question.", "sources": [], "chunks": []}

    kwargs = {} if top_k is None else {"top_k": top_k}
    chunks = retrieve(question, **kwargs)
    context = build_context(chunks)
    sources = _unique_sources(chunks)

    user_prompt = (
        f"DOCUMENT EXCERPTS:\n{context}\n\n"
        f"QUESTION: {question.strip()}\n\n"
        "ANSWER (use only the excerpts above):"
    )

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer = (response.choices[0].message.content or "").strip()

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What GPA is required to affiliate with Cornell INFO?"
    result = ask(q)
    print("Answer:\n", result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        print(f"  • {source}")
