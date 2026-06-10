"""
Milestone 3 — Document ingestion pipeline.

Loads sources from sources.json, fetches or reads raw content, cleans it,
and writes normalized .txt files to documents/cleaned/.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
SOURCES_PATH = ROOT / "sources.json"
RAW_DIR = ROOT / "documents" / "raw"
CLEAN_DIR = ROOT / "documents" / "cleaned"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; CornellINFOGuide/1.0; "
        "+https://github.com/educational-rag-project)"
    )
}

BOILERPLATE_PATTERNS = [
    r"cookie(s)? policy",
    r"sign up for",
    r"subscribe to",
    r"read more",
    r"share on",
    r"follow us",
    r"all rights reserved",
    r"skip to (main )?content",
    r"accept all cookies",
    r"^jump to ratings$",
    r"^load more ratings$",
    r"^similar professors$",
    r"^i'm professor",
    r"^rate$",
    r"^compare$",
    r"^would take again$",
    r"^level of difficulty$",
    r"^overall quality based on$",
    r"^all courses$",
    r"^for credit$",
    r"^attendance$",
    r"^textbook$",
    r"^grade$",
    r"^helpful$",
    r"^\d+$",
]


def load_sources() -> list[dict[str, Any]]:
    with SOURCES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def fetch_url(url: str, timeout: int = 30) -> str:
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def fetch_reddit_thread(reddit_id: str) -> str:
    """Fetch a Reddit thread via PullPush archive API."""
    submission_url = "https://api.pullpush.io/reddit/search/submission/"
    comments_url = "https://api.pullpush.io/reddit/search/comment/"

    submission_resp = requests.get(
        submission_url,
        params={"ids": f"t3_{reddit_id}"},
        headers=HEADERS,
        timeout=30,
    )
    submission_resp.raise_for_status()
    submissions = submission_resp.json().get("data", [])
    if not submissions:
        raise ValueError(f"No submission found for reddit id {reddit_id}")

    post = submissions[0]
    parts = [
        f"POST TITLE: {post.get('title', '').strip()}",
        f"SUBREDDIT: r/{post.get('subreddit', 'Cornell')}",
        "",
        f"POST BODY:\n{(post.get('selftext') or '').strip()}",
    ]

    comments_resp = requests.get(
        comments_url,
        params={"link_id": f"t3_{reddit_id}", "size": 100, "sort": "desc"},
        headers=HEADERS,
        timeout=30,
    )
    comments_resp.raise_for_status()
    comments = comments_resp.json().get("data", [])

    for comment in comments:
        body = (comment.get("body") or "").strip()
        if not body or body in ("[deleted]", "[removed]"):
            continue
        author = comment.get("author", "unknown")
        parts.extend(["", "---", f"COMMENT by u/{author}:", body, "---"])

    return "\n".join(parts).strip()


def html_to_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return normalize_text(text)


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines: list[str] = []
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            lines.append("")
            continue
        lower = line.lower()
        if any(re.search(pat, lower) for pat in BOILERPLATE_PATTERNS):
            continue
        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_main_content(raw_html: str, source_type: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")

    selectors_by_type = {
        "student_newspaper": ["article", ".entry-content", "main"],
        "official_department": ["main", "article", ".region-content"],
        "official_outcomes": ["main", "article", ".field--name-body"],
        "student_wiki": ["main", "article", ".markdown-section", "body"],
        "campus_news": ["main", "article", ".region-content"],
        "student_career_story": ["main", "article", ".entry-content"],
        "course_review_site": ["main", "body"],
        "professor_reviews": ["main", "body"],
        "admissions_forum": ["main", "article", ".topic-body", "body"],
    }

    for selector in selectors_by_type.get(source_type, ["main", "article", "body"]):
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 200:
            return html_to_text(str(node))

    return html_to_text(raw_html)


def fetch_discourse_thread(url: str) -> str:
    """Fetch all posts from a Discourse forum thread (e.g. College Confidential)."""
    json_url = url.rstrip("/") + ".json"
    response = requests.get(json_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    posts = data.get("post_stream", {}).get("posts", [])
    if not posts:
        raise ValueError(f"No posts in Discourse thread: {url}")

    title = data.get("title", "").strip()
    parts = [f"THREAD TITLE: {title}", ""]
    for i, post in enumerate(posts, 1):
        cooked_html = post.get("cooked", "")
        username = post.get("username", "unknown")
        body = html_to_text(cooked_html)
        if not body:
            continue
        parts.extend(["", "---", f"POST {i} by {username}:", body, "---"])
    return "\n".join(parts).strip()


def fetch_source_content(source: dict[str, Any]) -> str:
    if source.get("reddit_id"):
        return fetch_reddit_thread(source["reddit_id"])

    if source["source_type"] == "admissions_forum":
        return fetch_discourse_thread(source["source_url"])

    raw_html = fetch_url(source["source_url"])
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{source['id']}_raw.html"
    raw_path.write_text(raw_html, encoding="utf-8")

    return extract_main_content(raw_html, source["source_type"])


def prepend_metadata_header(source: dict[str, Any], body: str) -> str:
    prefix_parts = [
        f"SOURCE: {source['title']}",
        f"URL: {source['source_url']}",
        f"TYPE: {source['source_type']}",
    ]
    if source.get("course_code"):
        prefix_parts.append(f"COURSE: {source['course_code']}")
    prefix_parts.append("")
    return "\n".join(prefix_parts) + body


def ingest_source(source: dict[str, Any], force: bool = False) -> Path:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CLEAN_DIR / source["filename"]

    if out_path.exists() and not force:
        return out_path

    try:
        content = fetch_source_content(source)
    except Exception as exc:
        raise RuntimeError(f"Failed to ingest {source['filename']}: {exc}") from exc

    if len(content) < 100:
        raise RuntimeError(
            f"Ingested content for {source['filename']} is too short ({len(content)} chars)"
        )

    content = prepend_metadata_header(source, content)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def ingest_all(force: bool = False) -> list[Path]:
    paths: list[Path] = []
    failures: list[str] = []

    for source in load_sources():
        try:
            path = ingest_source(source, force=force)
            paths.append(path)
            print(f"✓ {source['filename']} ({path.stat().st_size} bytes)")
        except Exception as exc:
            failures.append(f"{source['filename']}: {exc}")
            print(f"✗ {source['filename']}: {exc}")

    if failures:
        print("\nFailures:")
        for item in failures:
            print(f"  - {item}")

    print(f"\nIngested {len(paths)}/{len(load_sources())} documents.")
    return paths


if __name__ == "__main__":
    ingest_all()
