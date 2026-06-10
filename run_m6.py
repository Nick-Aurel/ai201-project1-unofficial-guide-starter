#!/usr/bin/env python3
"""Milestone 6 — Full evaluation: all 5 planning questions + retrieval metadata."""

from __future__ import annotations

import json
from pathlib import Path

from query import ask
from retrieve import retrieve

EVAL = [
    {
        "id": 1,
        "question": "How many undergraduates are declared in Cornell's Information Science major, and what enrollment problem do students describe?",
        "expected": "Over 700 undergraduates. Students report difficulty enrolling in core INFO classes during add/drop, overcrowded office hours, and limited spring-semester availability for core requirements (most core courses offered in fall).",
    },
    {
        "id": 2,
        "question": "What GPA and course requirements must Cornell students meet to affiliate with the Information Science major?",
        "expected": "Minimum GPA of 2.50 in required courses with no grade below C; introductory programming (CS 1110 or CS 1112); calculus or statistics prerequisite; and completion of any 2 of the 5 INFO core courses before affiliating.",
    },
    {
        "id": 3,
        "question": "What technology and workload do students report for INFO 3300 (Visual Data Analytics for the Web)?",
        "expected": "D3.js for web-based data visualizations; roughly 6–8 programming assignments (often 3–4 hours each) plus two group projects; David Mimno is a common instructor and often teaches JavaScript from the basics.",
    },
    {
        "id": 4,
        "question": "For A&S Class of 2025 Information Science majors, what percentage were employed full-time six months after graduation, and which three sectors employed the largest shares?",
        "expected": "72% employed full-time. Largest sectors: technology (32%), financial services (31%), and management consulting (19%).",
    },
    {
        "id": 5,
        "question": "Is the Information Science major curriculum the same for students in CALS and CAS at Cornell?",
        "expected": "Yes — the INFO program and core major requirements are the same across colleges. The difference is each college's distribution and foundational requirements.",
    },
]

OUT_OF_SCOPE = "What is the best dining hall at Cornell?"
OUTPUT = Path(__file__).parent / "documents" / "evaluation_report_m6.json"


def main() -> None:
    report: list[dict] = []

    for item in EVAL:
        print(f"\n=== Eval Q{item['id']} ===")
        chunks = retrieve(item["question"])
        result = ask(item["question"])
        entry = {
            "id": item["id"],
            "question": item["question"],
            "expected_answer": item["expected"],
            "system_answer": result["answer"],
            "sources": result["sources"],
            "retrieval": [
                {
                    "distance": c["distance"],
                    "source_filename": c["metadata"].get("source_filename"),
                    "chunk_index": c["metadata"].get("chunk_index"),
                    "text_preview": c["text"][:300],
                }
                for c in chunks
            ],
        }
        report.append(entry)
        print(result["answer"][:400])
        print("Sources:", result["sources"])

    print("\n=== Out of scope ===")
    oos = ask(OUT_OF_SCOPE)
    report.append(
        {
            "id": "out_of_scope",
            "question": OUT_OF_SCOPE,
            "system_answer": oos["answer"],
            "sources": oos["sources"],
        }
    )
    print(oos["answer"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {OUTPUT}")


if __name__ == "__main__":
    main()
