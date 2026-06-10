# Reddit Research: Cornell Information Science

Research notes for Project 1 (The Unofficial Guide). Searched `r/cornell` via the PullPush Reddit archive API in June 2026, sorting by upvotes and comment activity across queries like "information science," "INFO major," "INFO 2950," "INFO 1300," "concentration," "internship," and "product management."

## Key finding

Dedicated Information Science threads on `r/cornell` are generally **low-traffic** (often 0–3 upvotes). One exception dominates: a tier-list post from an INFO grad with **172 upvotes and 35 comments**. For Reddit content, prioritize that post plus a few targeted threads on courses and careers.

---

## Selected for `planning.md`

These three were added to the Documents section (replacing College Confidential #3 and two Rate My Professors pages).

| # | Post | Engagement | URL |
|---|------|------------|-----|
| 1 | Tier List of Every Class I've Taken at Cornell | 172 up · 35 cmts | https://reddit.com/r/Cornell/comments/1kmjbs3/tier_list_of_every_class_ive_taken_at_cornell/ |
| 2 | Which Info Sci concentration for product management in tech? | 6 up · 4 cmts | https://reddit.com/r/Cornell/comments/10hj6vg/which_info_sci_concentration_for_product/ |
| 3 | Should I take CS 3780 (intro to ML) or Info 2950 (Intro to Data Science)? | 3 up · 1 cmt | https://reddit.com/r/Cornell/comments/1i1a7zb/should_i_take_cs_3780_intro_to_ml_or_info_2950/ |

### Why these three

**Tier list** — Author majored in Information Science (Data Science concentration). Ranks many INFO courses by tier (S through lower), including:

- INFO 2950 (Intro to Data Science) — Wilkens
- INFO 2040 (Networks) — Kleinberg & Easley
- INFO 3350 (Text Mining) — Wilkens
- INFO 4940 (Social Dynamics and Network Analytics) — Yian Yin
- INFO 1260 (Choices and Consequences in Computing) — Kleinberg & Levy
- INFO 4240 (Designing Tech for Social Impact) — Csikszentmihalyi
- INFO 2450 (Communication and Technology) — Chao Yu
- INFO 2770 (Computational Sustainability) — Carla Gomes

**PM concentration thread** — Direct INFO career-path question; complements the Unofficial Cornell CS Wiki internship source.

**CS 3780 vs INFO 2950** — Common course-path decision; useful for evaluation questions about data science vs. ML sequencing.

---

## Honorable mentions (not in planning.md)

| Post | Engagement | URL | Notes |
|------|------------|-----|-------|
| Tips for Breaking Into Product Management at Cornell? | 6 up · 0 cmts | https://reddit.com/r/Cornell/comments/1jc6m3j/tips_for_breaking_into_product_management_at/ | Sophomore INFO student asking about PM resources |
| Schedule for someone debating between CS and Info Sci in CAS | 0 up · 17 cmts | https://reddit.com/r/Cornell/comments/w0iadw/schedule_for_someone_debating_between_cs_and_info/ | High comment engagement; freshman scheduling |
| Need Advice on Fall 2024 Info Sci Schedule | 1 up · 7 cmts | https://reddit.com/r/Cornell/comments/1e6irox/need_advice_on_fall_2024_info_sci_schedule/ | Internal transfer into INFO (CALS); affiliation planning |
| overwhelmed — calling info sci majors | 0 up · 8 cmts | https://reddit.com/r/Cornell/comments/yp1erk/overwhelmed_help_a_girly_out_im_scared_im_alr/ | Freshman INFO scheduling anxiety |
| MPS in Information Science, is it worth it? | 4 up · 3 cmts | https://reddit.com/r/Cornell/comments/yfwhju/mps_in_information_science_is_it_worth_it/ | Grad program; skip unless covering post-grad |
| Go from CALS (info science) to CAS as a transfer student | 1 up · 0 cmts | https://reddit.com/r/Cornell/comments/1ko4sfv/go_from_cals_info_science_to_cas_as_a_transfe/ | College-switching within INFO |
| Internal Transfer Requirements | 3 up · 0 cmts | https://reddit.com/r/Cornell/comments/1hiu8o2/internal_transfer_requirements/ | General internal transfer |
| Anyone currently taking INFO 2950 with Soltoff? | 1 up · 0 cmts | https://reddit.com/r/Cornell/comments/1ajvkp5/anyone_currently_taking_info_2950_with_soltoff/ | Professor-specific; pairs with RMP Mimno/Koenecke |
| Should I skip info 1300? | 1 up · 0 cmts | https://reddit.com/r/Cornell/comments/1hl1igd/should_i_skip_info_1300/ | Core course waiver question |

---

## Sample evaluation questions these sources support

1. What do students say about INFO 2950 with Matthew Wilkens? *(tier list)*
2. Which INFO concentration do students recommend for product management in tech? *(PM thread)*
3. Should you take INFO 2950 before CS 3780, or the other way around? *(CS 3780 vs 2950 thread)*
4. What do students think of INFO 4240 (Designing Tech for Social Impact)? *(tier list)*
5. How do INFO students describe breaking into internships or PM roles? *(PM thread + CS Wiki)*

---

## Search methodology

- **API:** `https://api.pullpush.io/reddit/search/submission/` (Reddit's own JSON API blocked automated access during research)
- **Subreddit:** `r/cornell` (also spot-checked `r/ApplyingToCollege` — mostly admissions, not student experience)
- **Queries run:** `information science`, `INFO major`, `info sci`, `INFO 2950`, `INFO 1300`, `affiliation`, `Bowers`, `internal transfer`, `concentration`, `double major`, `product management`, `internship`, `CALS info`, `MPS information`
- **Ranking:** Combined score = upvotes + (comments × 2) for engagement signal

---

## Replaced in planning.md

| Removed | Reason |
|---------|--------|
| College Confidential — changing majors | Generic; tier list covers more INFO-specific student voice |
| Rate My Professors — Jeffery Rzeszotarski | Already have 2 other RMP pages; Reddit adds source variety |
| Rate My Professors — Ian Lundberg | Same; kept Mimno and Koenecke for INFO 2950/data science coverage |
