# The Unofficial Guide — Project 1

**Cornell Information Science** — a RAG system that makes student-sourced knowledge about the INFO major searchable: courses, professors, affiliation, enrollment, and careers.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # add GROQ_API_KEY from console.groq.com

python run_m3.py                   # ingest + chunk (first time)
python embed.py                    # embed into ChromaDB (first time)
python app.py                      # Gradio UI → http://localhost:7860
```

Pipeline scripts: `ingest.py`, `chunk.py`, `embed.py`, `retrieve.py`, `query.py`, `app.py`. Full eval: `python run_m6.py`.

---

## Domain

This system covers **Cornell Information Science — what students actually say about courses, professors, and building a career.** Official Cornell pages list degree requirements and course descriptions, but they do not capture exam difficulty, project load, teaching style, add/drop stress, or the practical advice seniors pass down on forums and wikis. This Unofficial Guide aggregates that scattered knowledge — Reddit threads, Rate My Professors reviews, the Cornell Daily Sun, student wikis, and official outcomes data — so a student can ask plain-language questions and get grounded, cited answers.

---

## Document Sources

Documents were collected from 15 sources across 7 types (forums, Reddit, student newspaper, official department pages, professor/course reviews, student wikis, career stories). Raw web pages were fetched with `ingest.py` (PullPush API for Reddit, Discourse JSON for College Confidential, BeautifulSoup for HTML). Cleaned text is saved in `documents/cleaned/`. Coursicle was saved manually after a 429 rate limit.

| # | Source | Type | URL or file path |
|---|--------|------|------------------|
| 1 | College Confidential — INFO in 3 colleges | Admissions forum | https://talk.collegeconfidential.com/t/cornell-information-science-in-3-different-colleges/1933450 |
| 2 | r/Cornell — class tier list | Reddit | https://reddit.com/r/Cornell/comments/1kmjbs3/tier_list_of_every_class_ive_taken_at_cornell/ |
| 3 | r/Cornell — CS 3780 vs INFO 2950 | Reddit | https://reddit.com/r/Cornell/comments/1i1a7zb/should_i_take_cs_3780_intro_to_ml_or_info_2950/ |
| 4 | Cornell Daily Sun — INFO growing pains | Student newspaper | https://cornellsun.com/2024/03/06/with-over-700-undergraduates-information-science-department-experiences-growing-pains-plans-to-streamline-major/ |
| 5 | Cornell Daily Sun — enrollment struggles | Student newspaper | https://www.cornellsun.com/article/2023/01/computer-and-information-science-students-struggle-with-course-enrollment-adding-stress-instead-of-classes |
| 6 | Cornell Bowers — INFO affiliation requirements | Official department | https://infosci.cornell.edu/bachelor-science-information-science/apply |
| 7 | Rate My Professors — David Mimno | Professor reviews | https://www.ratemyprofessors.com/professor/2119129 |
| 8 | Rate My Professors — Allison Koenecke | Professor reviews | https://www.ratemyprofessors.com/professor/2914049 |
| 9 | r/Cornell — INFO concentration for PM | Reddit | https://reddit.com/r/Cornell/comments/10hj6vg/which_info_sci_concentration_for_product/ |
| 10 | Coursicle — INFO 3300 | Course reviews | https://www.coursicle.com/cornell/courses/INFO/3300/ |
| 11 | Unofficial Cornell CS Wiki — INFO/CS 3300 | Student wiki | https://cornellcswiki.gitlab.io/classes/CS3300.html |
| 12 | Cornell A&S — INFO career outcomes | Official outcomes | https://as.cornell.edu/major_minor_gradfield/information-science |
| 13 | Unofficial Cornell CS Wiki — careers | Student wiki | https://cornellcswiki.gitlab.io/careers/opportunities.html |
| 14 | Entrepreneurship at Cornell — Jiang Fellows | Student career story | https://eship.cornell.edu/jiang-fellows-tell-all/ |
| 15 | Cornell Bowers — CHI 2026 research news | Campus news | https://infosci.cornell.edu/news-stories/cornell-researchers-contribute-more-40-papers-chi-2026 |

**Ingestion & cleaning:** `ingest.py` strips HTML tags, navigation, cookie banners, and boilerplate; normalizes whitespace and HTML entities; prepends metadata headers (`SOURCE`, `URL`, `TYPE`, `COURSE` where applicable). Reddit threads are fetched via the PullPush archive API with post + comment structure preserved.

---

## Chunking Strategy

**Chunk size:** 450 characters (~110 tokens), with whole-review preservation for short opinion text.

**Overlap:** 80 characters (~18% overlap on recursive splits).

**Why these choices fit your documents:** The corpus mixes short reviews (RMP, Coursicle), long Daily Sun articles, Reddit comment threads, and wiki/official reference pages. Fixed 450-char chunks with per-source rules keep reviews self-contained while breaking long articles into focused passages. Overlap helps when affiliation rules span two sentences (GPA threshold + core-course count). Per-source rules: whole reviews ≤450 chars; Reddit split on `---` comment boundaries; wikis/official pages split on headers; journalism split paragraph-first then fixed-size fallback.

**Preprocessing:** HTML stripped in ingestion; chunks under 50 characters discarded; each chunk tagged with `source_filename`, `source_url`, `source_type`, `chunk_index`, and `course_code` when known.

**Final chunk count:** **353 chunks** across 15 documents.

### Sample chunks (5)

**1. `04_daily_sun_info_growing_pains.txt` (chunk 1)**  
> With over 700 undergraduates declared in the major, information science is one of the largest fields of study at Cornell, according to Claire Cardie, associate dean for education at the Bowers College of Computing and Information Science.

**2. `06_bowers_info_affiliation.txt` (chunk 4)**  
> Applicants must meet all of the following requirements to be eligible to apply (also known as "affiliate"): General Requirement A grade point average of 2.50 or higher in the required courses listed below, with no single course grade below a "C" ("C-" does not count).

**3. `11_cswiki_info_3300.txt` (workload section)**  
> Several (6-8) programming assignments that generally don't take more than a few (3-4) hours. Some of them can be completed in as little as 30 minutes. Two group projects with randomized groups of 3.

**4. `07_rmp_david_mimno.txt` (INFO 2950 review)**  
> Had this guy for INFO 2950. Maybe I just liked the material, but I found his lectures to be super interesting and engaging. Hopefully I can take another one of his classes before I graduate.

**5. `01_college_confidential_info_three_colleges.txt` (POST 2)**  
> The info sci program will be the same regardless of the college; the difference is in the individual college requirements. Look at the requirements for each of them and see if one best fits what you're looking for.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional embeddings, runs locally).

**Why this model:** Project default; fast on CPU, no API key, no rate limits. Sufficient for English student text and short queries at our corpus scale (353 chunks).

**Production tradeoff reflection:** For a production Cornell INFO guide, I would weigh: (1) **domain-specific accuracy** — a larger model like `e5-large-v2` may better separate course codes (INFO 3300 vs INFO 2950); (2) **context length** — longer inputs could embed full wiki sections without splitting stats tables; (3) **multilingual support** — not critical now but relevant for international student forums; (4) **latency** — MiniLM is fast locally; API embeddings add network cost but scale better; (5) **privacy** — local embeddings keep student forum text on-device.

### Retrieval test examples

**Query 1:** *How many undergraduates are declared in Cornell's Information Science major, and what enrollment problem do students describe?*

| Rank | Source | Distance | Excerpt |
|------|--------|----------|---------|
| 1 | `04_daily_sun_info_growing_pains.txt` | 0.273 | "With over 700 undergraduates declared in the major…" |
| 2 | `05_daily_sun_enrollment_struggles.txt` | 0.283 | "Last fall, five out of the six information science core classes were offered in the fall semester, while only two are being taught this spring…" |

*Why relevant:* Both chunks directly address INFO major size and enrollment pain — the 700+ headcount and spring-semester core course scarcity match the question.

**Query 2:** *What GPA and course requirements must Cornell students meet to affiliate with the Information Science major?*

| Rank | Source | Distance | Excerpt |
|------|--------|----------|---------|
| 1 | `06_bowers_info_affiliation.txt` | 0.244 | "Applicants must meet all of the following requirements to be eligible to apply (also known as 'affiliate')…" |
| 2 | `06_bowers_info_affiliation.txt` | 0.256 | "grade point average of 2.50 or higher…" |

*Why relevant:* All top-5 results come from the official Bowers affiliation page — the authoritative source for GPA and course rules.

**Query 3:** *What technology and workload do students report for INFO 3300?*

| Rank | Source | Distance | Excerpt |
|------|--------|----------|---------|
| 1 | `10_coursicle_info_3300.txt` | 0.422 | "D3 Javascript library to develop static and dynamic visualizations…" |
| 2 | `11_cswiki_info_3300.txt` | 0.423 | "main technology used is D3.js" |

*Why relevant:* Top results are INFO-3300-specific course sources mentioning D3.js. Distances are higher than Q1–Q2 (0.42 vs ~0.24) because the query combines technology + workload, and the workload chunk lives in a separate CS Wiki section that ranked lower.

---

## Grounded Generation

**System prompt grounding instruction** (`query.py`):

```
You are The Unofficial Guide for Cornell Information Science.

Rules (follow strictly):
1. Answer ONLY using facts stated in the provided document excerpts.
2. Do NOT use general knowledge, assumptions, or information not present in the excerpts.
3. If the excerpts do not contain enough information to answer the question, respond with exactly:
   "I don't have enough information on that."
4. Be concise and specific. Mention course codes, numbers, or professor names only when they appear in the excerpts.
5. Do not invent sources or statistics.
```

**Structural choices:** Retrieved chunks are labeled `[Document N: filename (Official / Student forum / …)]` before being passed to the LLM. Temperature is set to 0.1. The LLM generates the answer; **sources are attached programmatically** from retrieval metadata (deduplicated `source_filename` list), displayed in a separate Gradio field — not left to the model alone.

**How source attribution is surfaced in the response:** The Gradio UI shows two outputs: **Answer** (LLM text grounded in context) and **Retrieved from** (bullet list of source filenames, e.g. `• 05_daily_sun_enrollment_struggles.txt`).

### Example grounded responses

**Example 1 — Eval Q1**

- **Question:** How many undergraduates are declared in Cornell's Information Science major, and what enrollment problem do students describe?
- **Answer:** There are over 700 undergraduates declared in the Information Science major. Students describe the enrollment problem as it being "near impossible to enroll in the classes and to be in the major" due to limited course offerings and large class sizes.
- **Retrieved from:** `05_daily_sun_enrollment_struggles.txt`, `04_daily_sun_info_growing_pains.txt`

**Example 2 — Eval Q4**

- **Question:** For A&S Class of 2025 Information Science majors, what percentage were employed full-time six months after graduation, and which three sectors employed the largest shares?
- **Answer:** 72% employed full-time. Largest sectors: technology (32%), financial services (31%), management consulting (19%).
- **Retrieved from:** `12_as_info_career_outcomes.txt`

### Out-of-scope example

- **Question:** What is the best dining hall at Cornell?
- **Answer:** I don't have enough information on that.
- **Retrieved from:** `02_reddit_class_tier_list.txt`, `01_college_confidential_info_three_colleges.txt` (loosely related chunks retrieved, but the model correctly refused to answer)

---

## Query Interface

**Tool:** Gradio web UI (`app.py`). Run with `python app.py` → `http://localhost:7860`.

| Field | Description |
|-------|-------------|
| **Your question** | Text input — user types a natural-language question about Cornell INFO |
| **Ask** | Button (or press Enter) to submit |
| **Answer** | Grounded response generated from retrieved chunks only |
| **Retrieved from** | Bullet list of source filenames used for retrieval |

**Sample interaction:**

```
Your question:  What GPA is required to affiliate with Cornell INFO?

Answer:         To affiliate with the Information Science major, Cornell students must meet
                a grade point average of 2.50 or higher in the required courses, with no
                single course grade below a "C" ("C-" does not count), and complete
                Introductory Programming (CS 1110 or CS 1112)...

Retrieved from: • 06_bowers_info_affiliation.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How many undergraduates are declared in INFO, and what enrollment problem do students describe? | 700+ majors; difficulty enrolling in core classes, add/drop stress, limited spring offerings | 700+ undergraduates; "near impossible to enroll in classes" due to limited offerings and large class sizes | Relevant | Accurate |
| 2 | What GPA and course requirements for INFO affiliation? | 2.50 GPA, no grade below C, CS 1110/1112, calc/stats, 2 of 5 core INFO courses | 2.50 GPA, no C- grades, CS 1110/1112 — **missing** "2 of 5 core courses" and calc/stats | Relevant | Partially accurate |
| 3 | INFO 3300 technology and workload? | D3.js; 6–8 assignments (3–4 hrs); two group projects; Mimno teaches JS basics | D3.js and SVG covered correctly; model stated **no workload information** in excerpts | Partially relevant | Partially accurate |
| 4 | A&S 2025 INFO employment % and top 3 sectors? | 72% employed; tech 32%, finance 31%, consulting 19% | 72% full-time; all three sector percentages correct | Relevant | Accurate |
| 5 | Is INFO curriculum the same for CALS and CAS? | Yes — same INFO core; difference is college distribution requirements | Hedged, then incorrectly ended with refusal despite relevant chunks being retrieved | Partially relevant | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

Full machine-readable results: `documents/evaluation_report_m6.json`.

---

## Failure Case Analysis

**Question that failed:** Is the Information Science major curriculum the same for students in CALS and CAS at Cornell?

**What the system returned:** The model hedged ("excerpts do not explicitly state…"), discussed "Degree Differences" from the Bowers page, and ultimately responded with *"I don't have enough information on that"* — even though College Confidential contains a direct answer: *"The info sci program will be the same regardless of the college."*

**Root cause (tied to a specific pipeline stage):** **Retrieval + chunking.** The top retrieved chunk was `06_bowers_info_affiliation.txt` chunk 13 ("Degree Differences" / "Degree Similarities"), which discusses engineering vs CALS vs A&S in administrative language. The clearest student answer lives in `01_college_confidential_info_three_colleges.txt` **POST 2** (chunk index 1), but retrieval ranked POST 1 (the original question) and Bowers official text higher. The LLM saw conflicting official "differences" language without the concise forum quote in its top-5 context, so generation failed to produce the correct yes/no answer.

**What you would change to fix it:** (1) Boost student-forum chunks when queries mention "same" or college comparison; (2) merge each College Confidential post with its thread context so OP questions and answers aren't competing chunks; (3) add metadata filtering (`source_type=admissions_forum`) for college-choice queries.

*Secondary failure (Q3):* CS Wiki workload text (*"6-8 programming assignments…"*) exists in chunk index 2 but ranked below the shorter D3.js line chunk — a retrieval ranking issue within the same document.

---

## Spec Reflection

**One way the spec helped you during implementation:** The per-source chunking table in `planning.md` (reviews vs Reddit vs wikis vs journalism) translated directly into `chunk.py` branching logic. Without specifying those rules upfront, a generic 500-char splitter would have shredded RMP reviews and split College Confidential posts mid-thread — exactly the failure modes the spec anticipated.

**One way your implementation diverged from the spec, and why:** The spec assumed Coursicle would be scraped automatically, but Coursicle returned HTTP 429. I saved a manual `10_coursicle_info_3300.txt` from fetched content instead. I also added `@lru_cache` on the embedding model in `embed.py` (not in the original architecture diagram) because reloading `all-MiniLM-L6-v2` on every Gradio query made the UI unusably slow.

---

## AI Usage

**Instance 1 — Milestone 3 ingestion & chunking**

- *What I gave the AI:* The Documents table and Chunking Strategy from `planning.md`, plus Milestone 3 requirements from `instructions-project1.pdf`.
- *What it produced:* Initial `ingest.py` and `chunk.py` with BeautifulSoup cleaning, PullPush Reddit fetching, and per-source splitters.
- *What I changed or overrode:* Added Discourse JSON fetching for College Confidential (HTML only returned the first post). Manually created Coursicle after rate limiting. Tightened RMP review splitting to one-chunk-per-review. Reduced boilerplate filters after inspecting raw RMP output.

**Instance 2 — Milestones 4–5 embedding, retrieval, and generation**

- *What I gave the AI:* Retrieval Approach section, architecture diagram, grounding requirements, and Gradio skeleton from the project instructions.
- *What it produced:* `embed.py`, `retrieve.py`, `query.py`, and `app.py` with ChromaDB cosine search, Groq `llama-3.3-70b-versatile`, and programmatic source lists.
- *What I changed or overrode:* Pinned `numpy<2` after a torch compatibility error. Added source-type labels (`Official` vs `Student forum`) in the prompt context. Set temperature to 0.1 (not the AI's default 0.7). Cached the embedding model with `lru_cache` after timing tests showed 3+ minute response times without it.
