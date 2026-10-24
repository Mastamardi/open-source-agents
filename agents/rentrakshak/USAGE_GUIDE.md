# RentRakshak — How to Use (Quick Guide)

This guide helps you run the hackathon demo without last-minute surprises.

**Judges:** start with **[JUDGING_OVERVIEW.md](JUDGING_OVERVIEW.md)** and the long-form **[README.md](README.md)** (full feature descriptions). This file is the command cheat sheet.

## 1. One-time setup

```bash
cd agents/rentrakshak
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env        # optional: add GOOGLE_API_KEY for live ADK chat
python scripts/seed_demo_data.py
```

## 2. Run tests (no API key, no internet)

```bash
pytest -q
```

Expected: **32 passed**.

## 3. Deterministic safety report (recommended for judges)

No LLM — same input always yields the same rule findings.

```bash
python main.py --listing @tests/fixtures/suspicious_listing.txt
python main.py --listing @tests/fixtures/clean_listing.txt
```

## 4. Streamlit UI (full product demo)

```bash
streamlit run ui/streamlit_app.py
```

Open the URL shown (usually http://localhost:8501).

| Tab | What to try |
|-----|-------------|
| Analyze listing | Paste `tests/fixtures/suspicious_listing.txt` content |
| Tenant experiences | Search Koramangala after seed script |
| Vacating / rooms | Search Whitefield for seeded room |
| Karnataka checklist | Scroll sources — not legal advice |

## 5. Google ADK agent (needs `GOOGLE_API_KEY`)

From `agents/rentrakshak`:

```bash
export GOOGLE_API_KEY=your_key
adk run adk_agent
# or
adk web adk_agent
```

Example prompts:

- "Analyze this listing and give evidence-backed risks: [paste text]"
- "Estimate rent for 2 BHK semi-furnished in Whitefield using your tool"
- "What should I verify before paying deposit in Karnataka?"

The agent must call tools for rents, risks, and legal references — it should not invent figures.

## 6. Reset demo database

```bash
rm -f data/rentrakshak.db
python scripts/seed_demo_data.py
```

## 7. Optional: Gemma / Vertex

Set in `.env` (see `.env.example`). Not required for pytest or Streamlit deterministic flows.

## 8. Optional: Model Armor

Set `MODEL_ARMOR_PROJECT_ID` and `MODEL_ARMOR_TEMPLATE_ID`. If unset, local guardrails still run (see `rentrakshak/guardrails/`).

## 9. Pull request / upstream

Project path: `agents/rentrakshak/` in [gdgcblr/open-source-agents](https://github.com/gdgcblr/open-source-agents).

For manual QA before presenting, follow **FEATURE_VERIFICATION_GUIDE.md** section by section.
