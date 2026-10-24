# RentRakshak — Judging overview (read this first)

One-page narrative for evaluators who may not run the code immediately.

## Elevator pitch

**RentRakshak** helps Bengaluru renters **before they pay a deposit**. It combines a **Google ADK** agent with **deterministic** safety tools, an **anonymous tenant community**, and a **vacating-room board**—so the demo is a product, not a generic chat wrapper.

**Tagline:** Rent smarter. Stay safer. Help the next tenant.

## Five headline features

1. **Rental safety agent** — structured report from listing + chat; rule IDs, severities, evidence excerpts, verification steps.  
2. **Rent estimator** — min/median/max from versioned JSON; says when data is insufficient instead of guessing.  
3. **Anonymous experiences** — moderated posts; PII redaction; negative-but-fair reviews allowed.  
4. **Vacating board** — active/filled/expired lifecycle; contact kept private in MVP.  
5. **Karnataka checklist** — practical steps + legal source links; no invented deposit cap.

## Differentiators for scoring

| Criterion | Evidence in repo |
|-----------|------------------|
| **Google ADK depth** | `rentrakshak/agent.py`, `adk_agent/`, 13 `FunctionTool`s |
| **AI safety** | `guardrails/content_safety.py`, injection in fixtures, 32 tests |
| **Responsible claims** | Limitations on every report; low risk ≠ verified |
| **Real persistence** | SQLite schema for experiences & vacating posts |
| **Reproducibility** | `pytest -q` without network or API key |
| **Documentation** | README, USAGE_GUIDE, FEATURE_VERIFICATION_GUIDE (Sections A–I) |

## 3-minute demo script

1. `cd agents/rentrakshak && pytest -q`  
2. `python main.py --listing @tests/fixtures/suspicious_listing.txt` — point at RF-005 and critical risk.  
3. `streamlit run ui/streamlit_app.py` — Analyze tab + Community (Koramangala) + Vacating (Whitefield).  
4. Optional: `adk web adk_agent` with `GOOGLE_API_KEY` — show tool calls.  
5. Say clearly: rent JSON is **demo-labeled**; community posts are **unverified**; RentRakshak is **not** Google/government.

## Where to look in code

| Topic | Path |
|-------|------|
| Agent instructions | `rentrakshak/agent.py` |
| Red-flag rules | `rentrakshak/services/risk_rules.py` |
| Full report | `rentrakshak/services/safety_report.py` |
| Community | `rentrakshak/services/community.py` |
| Vacating | `rentrakshak/services/vacating.py` |
| Tests | `tests/test_integration.py` |

## Pull request

Submitted to `gdgcblr/open-source-agents` from branch `feat/rentrakshak`.
