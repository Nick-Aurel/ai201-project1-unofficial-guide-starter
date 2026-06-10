#!/usr/bin/env python3
"""Run Milestone 4: embed chunks, then test retrieval on eval questions 1–3."""

from __future__ import annotations

import json
from pathlib import Path

from embed import embed_chunks
from retrieve import print_retrieval_results, retrieve

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": (
            "How many undergraduates are declared in Cornell's Information Science major, "
            "and what enrollment problem do students describe?"
        ),
    },
    {
        "id": 2,
        "question": (
            "What GPA and course requirements must Cornell students meet to affiliate "
            "with the Information Science major?"
        ),
    },
    {
        "id": 3,
        "question": (
            "What technology and workload do students report for INFO 3300 "
            "(Visual Data Analytics for the Web)?"
        ),
    },
]

OUTPUT_PATH = Path(__file__).parent / "documents" / "retrieval_tests_m4.json"


def main() -> None:
    print("=== Milestone 4: Embedding ===\n")
    count = embed_chunks(reset=True)
    print(f"Embedded {count} chunks.\n")

    print("=== Milestone 4: Retrieval tests (eval Q1–Q3) ===\n")
    report: list[dict] = []

    for item in EVAL_QUESTIONS:
        results = retrieve(item["question"])
        print_retrieval_results(item["question"], results)

        best = results[0] if results else None
        report.append(
            {
                "eval_id": item["id"],
                "question": item["question"],
                "top_result": {
                    "distance": best["distance"] if best else None,
                    "source_filename": best["metadata"].get("source_filename") if best else None,
                    "text_preview": (best["text"][:400] if best else None),
                },
                "all_results": [
                    {
                        "distance": r["distance"],
                        "source_filename": r["metadata"].get("source_filename"),
                        "chunk_index": r["metadata"].get("chunk_index"),
                    }
                    for r in results
                ],
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n\nSaved retrieval report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
