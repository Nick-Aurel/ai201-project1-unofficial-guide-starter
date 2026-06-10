#!/usr/bin/env python3
"""Run Milestone 5 smoke tests: eval questions 1–3 + out-of-scope refusal."""

from __future__ import annotations

import json
from pathlib import Path

from query import REFUSAL_PHRASE, ask

EVAL_QUESTIONS = [
    "How many undergraduates are declared in Cornell's Information Science major, and what enrollment problem do students describe?",
    "What GPA and course requirements must Cornell students meet to affiliate with the Information Science major?",
    "What technology and workload do students report for INFO 3300 (Visual Data Analytics for the Web)?",
]

OUT_OF_SCOPE = "What is the best dining hall at Cornell?"

OUTPUT_PATH = Path(__file__).parent / "documents" / "generation_tests_m5.json"


def main() -> None:
    report: list[dict] = []

    print("=== Milestone 5: Grounded generation tests ===\n")

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        print(f"--- Eval Q{i} ---")
        result = ask(question)
        print(f"Q: {question}\n")
        print(f"A: {result['answer']}\n")
        print(f"Sources: {', '.join(result['sources'])}\n")
        report.append(
            {
                "type": "eval",
                "eval_id": i,
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"],
            }
        )

    print("--- Out-of-scope test ---")
    oos = ask(OUT_OF_SCOPE)
    print(f"Q: {OUT_OF_SCOPE}\n")
    print(f"A: {oos['answer']}\n")
    refused = REFUSAL_PHRASE.lower() in oos["answer"].lower()
    print(f"Refusal detected: {refused}\n")
    report.append(
        {
            "type": "out_of_scope",
            "question": OUT_OF_SCOPE,
            "answer": oos["answer"],
            "sources": oos["sources"],
            "refusal_detected": refused,
        }
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Saved report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
