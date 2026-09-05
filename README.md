# ChemQuest — Duolingo-Style Chemistry Quiz App

A Flask web app that turns your chemistry notes (PDF / TXT / MD / DOCX) into a
Duolingo-style quiz game: XP, streaks, levels, topic mastery, timed questions,
instant feedback, confetti perfect-rounds, and a review screen.

**410 exam-ready questions with explanations** ship built-in: 353 chemistry across 9 topics
(Alcohols, Chemical Kinetics, Electrochemistry, Ethers, Haloalkanes, HaloArenes,
Nuclear Chemistry, Phenols, Transition Metals) plus 30 physics and 27 math.

## Quick start

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000  ->  /health for a health check
```

Hit **Start Mixed Quiz** (or tap a topic card to drill it) — no login needed.
Every answer shows an explanation, and option order is shuffled on every attempt.

## Study notes + OCR pipeline

Put files in `notes/` (PDF, TXT, MD, DOCX). The repo's 9 chemistry PDFs already
live there. Most are **scanned-image PDFs**, so the extractor:

1. Reads every page with PyMuPDF (`fitz`); falls back to `pypdf`.
2. Any page with < 50 chars of text is treated as a scanned image: it is
   rendered, pre-processed (grayscale → autocontrast → sharpen, with a
   binarized retry pass) and OCR'd with Tesseract via `pytesseract`.
3. All pages are concatenated in order and cached to `data/extracted/*.txt`;
   pages that fail both paths are logged with page numbers.
4. Without the OCR stack installed, image pages are logged as
   `ocr-missing` instead of crashing — the app always boots.

Install the OCR stack:

```bash
# system binary (Ubuntu/Debian)
sudo apt install tesseract-ocr
# python packages
pip install PyMuPDF pytesseract Pillow pypdf python-docx
```

Re-process documents via the admin endpoint (local-only unless `ADMIN_KEY` matches):

```
GET /admin/process-docs?key=YOUR_ADMIN_KEY
```

## Scoring

| Event | Reward |
|---|---|
| Correct answer | +10 XP |
| Every 3-in-a-row streak | +5 XP bonus |
| Perfect round (10/10) | +20 XP bonus |
| Level | 1 + total_XP // 100 |
| Day streak | +1 per consecutive day with a completed quiz |
| Daily goal | answer 10 questions |

## Project layout

```
app.py                 # Flask app: auth, quiz flow, scoring, APIs, admin
models.py              # SQLAlchemy: User, Question, Document, UserProgress
document_processor.py  # per-page text extraction + OCR + caching
question_generator.py  # curated bank + chunk-based generation helpers
utils.py               # topic maps, question-bank JSON IO
data/questions.json    # 300-question bank, one JSON object per line (auto-loaded into SQLite)
data/extra_a.json      # curated extension bank, part 1
data/extra_b.json      # curated extension bank, part 2
data/quiz.db           # SQLite DB (created on first run)
templates/             # base, index, dashboard, quiz, complete, review
static/                # css + vanilla JS (30 s timer, animations, confetti)
notes/                 # your study materials
```

## API

- `GET /health` → `{"status":"ok"}`
- `GET /api/topics` → topics + question counts
- `GET /api/questions` → all questions (id/text/topic/difficulty)
- `GET /api/questions/<topic>` → full questions for a topic
- `GET /quiz/next` → current question JSON · `POST /quiz/submit` → answer

## Tests

```bash
python3 .swarm/test_e2e.py   # 24 end-to-end checks: auth, quiz, XP, review
```

## Notes

- Quiz sessions are 10 questions, mixed topics/difficulties (or one topic).
- Timer: 30 s per question, then the question counts as wrong and you advance.
- Fill-in-blank and True/False render as tappable word-bank options.
