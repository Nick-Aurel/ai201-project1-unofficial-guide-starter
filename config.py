"""Shared RAG pipeline configuration."""

from pathlib import Path

ROOT = Path(__file__).parent

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "cornell_info_guide"
CHROMA_PATH = ROOT / "chroma_db"
CHUNKS_PATH = ROOT / "documents" / "chunks.json"
TOP_K = 5

GROQ_MODEL = "llama-3.3-70b-versatile"
REFUSAL_PHRASE = "I don't have enough information on that."

SOURCE_TYPE_LABELS = {
    "official_department": "Official",
    "official_outcomes": "Official",
    "campus_news": "Official",
    "student_newspaper": "Student newspaper",
    "reddit": "Student forum",
    "admissions_forum": "Student forum",
    "professor_reviews": "Student review",
    "course_review_site": "Student review",
    "student_wiki": "Student wiki",
    "student_career_story": "Student story",
}
