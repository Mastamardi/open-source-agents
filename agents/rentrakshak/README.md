# RentRakshak

> **Rent smarter. Stay safer. Help the next tenant.**

Bengaluru-focused rental safety agent and anonymous tenant community, built for the [GDG Cloud Bengaluru open-source-agents](https://github.com/gdgcblr/open-source-agents) hackathon.

## Problem

Students, interns, and relocators in Bengaluru face rental scams, unclear deposits, and one-sided agreements. RentRakshak combines **evidence-based risk checks**, **transparent rent comparables**, **anonymous experiences**, and **vacating-room leads** — orchestrated by a **Google ADK** agent when an API key is available.

## Features

1. **AI rental safety agent** — listing + chat analysis, structured risk report, verification actions  
2. **Bengaluru rent estimator** — min/median/max from versioned JSON comparables (illustrative + demo listings)  
3. **Anonymous tenant experiences** — submit, moderate, search (SQLite)  
4. **Vacating / availability board** — draft → active → filled/withdrawn/expired  
5. **Karnataka rental checklist** — source-backed references, no invented deposit caps  
6. **Guardrails** — prompt-injection handling, PII redaction, abuse rejection; optional Model Armor hook  

## Technical stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Agent framework | [Google ADK](https://google.github.io/adk-docs/) (`google-adk`) |
| Model (orchestration) | `gemini-2.0-flash` via `GOOGLE_API_KEY` (optional for tests) |
| Validation | Pydantic v2 |
| Persistence | SQLite |
| UI | Streamlit |
| Tests | pytest (offline) |

Deterministic rules, rent math, moderation, and SQL run **without** the LLM. The model does not override security decisions.

## Architecture

```
User (Streamlit / adk run / main.py)
        │
        ▼
┌───────────────────┐
│  ADK root_agent   │  ← optional Gemini orchestration
└─────────┬─────────┘
          │ FunctionTools
          ▼
┌─────────────────────────────────────────────┐
│ analyze_* │ risk │ rent │ community │ vacate │
│ checklist │ safety_report │ guardrails      │
└─────────┬───────────────────────────────────┘
          │
          ▼
   SQLite + JSON datasets (rent, legal sources)
```

## Installation

```bash
cd agents/rentrakshak
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
python scripts/seed_demo_data.py
```

## Commands

| Goal | Command |
|------|---------|
| Tests | `pytest -q` |
| Safety report (no API key) | `python main.py --listing @tests/fixtures/suspicious_listing.txt` |
| Streamlit UI | `streamlit run ui/streamlit_app.py` |
| ADK CLI | `adk run adk_agent` or `adk web adk_agent` |
| Reset demo DB | `rm -f data/rentrakshak.db && python scripts/seed_demo_data.py` |

See **[USAGE_GUIDE.md](USAGE_GUIDE.md)** and **[FEATURE_VERIFICATION_GUIDE.md](FEATURE_VERIFICATION_GUIDE.md)**.

## Model setup

- **Gemini (default):** set `GOOGLE_API_KEY` in `.env`.  
- **Gemma on Vertex (optional):** see `.env.example`; not required for unit tests.  
- **Offline:** `main.py`, Streamlit analyze tab, and pytest use deterministic services only.

## Community privacy & moderation

- No legal name, email, or phone required to post.  
- Phone/email in text is redacted or held; threats rejected.  
- Public search returns **published** posts only; `edit_token` is secret.  
- Posts are **user-submitted experiences**, not verified facts.  
- Metadata (timestamps) may limit perfect anonymity — see About tab.

## Data methodology

- `data/rent_comparables.json` — labeled `illustrative_sample` or `observed_listing` (fictional demo URLs).  
- Estimates are **asking rents**, not transactions.  
- `data/legal_sources.json` — starting references; confirm with authorities or counsel.

## Security limitations

- Local guardrails reduce risk; they do not eliminate prompt injection.  
- Model Armor is optional and not enabled by default.  
- No property or owner is verified by RentRakshak.  
- Do not commit `.env` or `*.db`.

## Future work

- Full in-app contact relay, rate limiting, admin moderation UI  
- Richer comparables with licensed data feeds  
- Live Model Armor client wiring  

## Contributing

Follow the repo [CONTRIBUTING.md](../../CONTRIBUTING.md). Changes stay under `agents/rentrakshak/`.

## License

MIT (repository root).
