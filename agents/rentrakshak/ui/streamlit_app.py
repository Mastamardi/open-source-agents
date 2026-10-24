"""RentRakshak Streamlit demo UI."""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rentrakshak.db.database import init_db
from rentrakshak.models.schemas import AnonymousExperienceInput, RiskCategory, VacatingPostInput
from rentrakshak.services.checklist import build_rental_checklist, get_karnataka_rental_guidance
from rentrakshak.services.community import create_anonymous_experience, search_anonymous_experiences
from rentrakshak.services.safety_report import generate_rental_safety_report
from rentrakshak.services.vacating import create_vacating_post, search_available_rooms

RISK_STYLE = {
    RiskCategory.LOW.value: ("🟢", "#0d7a4a", "Low concern"),
    RiskCategory.NEEDS_VERIFICATION.value: ("🟡", "#b8860b", "Needs verification"),
    RiskCategory.HIGH.value: ("🟠", "#c45c00", "High concern"),
    RiskCategory.CRITICAL.value: ("🔴", "#b00020", "Critical warning"),
}

st.set_page_config(
    page_title="RentRakshak",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .tagline { color: #555; font-size: 1.05rem; margin-bottom: 1rem; }
    .risk-box {
        padding: 1rem 1.2rem; border-radius: 8px; margin: 1rem 0;
        border-left: 6px solid #333;
    }
    .step-card {
        background: #f8f9fa; padding: 0.9rem 1rem; border-radius: 8px;
        margin-bottom: 0.5rem; border: 1px solid #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

# ——— Sidebar: how to use (always visible) ———
with st.sidebar:
    st.markdown("### How to use")
    st.markdown(
        """
        1. **Setup once** (terminal):
        ```
        cd agents/rentrakshak
        source .venv/bin/activate
        pip install -e .
        python scripts/seed_demo_data.py
        streamlit run ui/streamlit_app.py
        ```
        2. Pick a page below ⬇️  
        3. **Check listing** → load sample scam text → **Run check**  
        4. **Community** → search `Koramangala` or `Whitefield`  
        5. No API key needed for this UI.
        """
    )
    st.divider()
    page = st.radio(
        "Go to",
        [
            "Start here",
            "Check a listing",
            "Tenant stories",
            "Rooms vacating soon",
            "Before you sign",
            "Privacy & tech",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("Load demo database", use_container_width=True):
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_demo_data.py")], check=False)
        st.success("Demo data refreshed. Search Koramangala / Whitefield.")

# ——— Header ———
st.markdown('<p class="main-header">RentRakshak</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Rent smarter. Stay safer. Help the next tenant.</p>',
    unsafe_allow_html=True,
)

if page == "Start here":
    st.markdown("#### Before you pay a deposit, check the risks.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="step-card"><b>1. Check listing</b><br>Paste portal text + WhatsApp chat. Get red flags with evidence.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="step-card"><b>2. Read tenant stories</b><br>Anonymous experiences by locality (demo: Koramangala).</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="step-card"><b>3. Find vacating rooms</b><br>Tenant-posted availability (demo: Whitefield).</div>', unsafe_allow_html=True)

    st.info("**No Gemini key required** — listing check uses rule-based tools in Python, not a live chat model.")
    st.markdown("**Try in 30 seconds:** sidebar → **Check a listing** → **Load suspicious sample** → **Run check**.")

    with st.expander("Command-line alternative (same engine)"):
        st.code(
            f"cd {ROOT}\npython main.py --listing @tests/fixtures/suspicious_listing.txt",
            language="bash",
        )

elif page == "Check a listing":
    st.markdown("Paste a **99acres / MagicBricks / WhatsApp** message. Add broker chat if you have it.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Load suspicious sample", use_container_width=True):
            st.session_state["listing_text"] = (FIXTURES / "suspicious_listing.txt").read_text()
    with col_b:
        if st.button("Load normal sample", use_container_width=True):
            st.session_state["listing_text"] = (FIXTURES / "clean_listing.txt").read_text()

    listing = st.text_area(
        "Listing",
        height=180,
        value=st.session_state.get("listing_text", ""),
        placeholder="2 BHK Koramangala, rent 15000, deposit...",
        key="listing_area",
    )
    chat = st.text_area("Landlord / broker chat (optional)", height=100, placeholder="Pay token today, send OTP...")
    locality = st.text_input("Locality hint if not in text", placeholder="e.g. HSR Layout")

    if st.button("Run check", type="primary", use_container_width=True):
        if not listing.strip():
            st.error("Paste something in the listing box first.")
        else:
            report = generate_rental_safety_report(
                listing, chat or None, locality_hint=locality or None
            )
            icon, color, label = RISK_STYLE.get(
                report.risk_category.value,
                ("⚪", "#333", report.risk_category.value),
            )
            st.markdown(
                f'<div class="risk-box" style="border-left-color:{color};">'
                f"<h3>{icon} {label}</h3>"
                f"<p>{report.risk_reasoning}</p></div>",
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Red flags found", len(report.findings))
            m2.metric("Locality", report.property.locality or "—")
            m3.metric(
                "Rent in text",
                f"₹{report.property.monthly_rent_inr}" if report.property.monthly_rent_inr else "—",
            )

            if report.findings:
                st.markdown("#### What we found (with evidence from your text)")
                for f in report.findings:
                    with st.container(border=True):
                        st.markdown(f"**{f.rule_id}** · {f.severity.value.upper()}")
                        st.write(f.explanation)
                        st.caption(f'Evidence: "{f.evidence_excerpt[:280]}…"' if len(f.evidence_excerpt) > 280 else f'Evidence: "{f.evidence_excerpt}"')
                        st.markdown(f"*Next step:* {f.recommended_next_step}")

            if report.rent_estimate:
                re = report.rent_estimate
                st.markdown("#### Rent benchmark (demo dataset only)")
                if re.sufficient_data:
                    st.success(
                        f"₹{re.rent_min_inr:,} – ₹{re.rent_max_inr:,} / month "
                        f"(median ₹{re.rent_median_inr:,}, {re.comparable_count} comparables)"
                    )
                else:
                    st.warning("Not enough comparables in our dataset — we will **not** guess a market rent.")
                for lim in re.limitations:
                    st.caption(lim)

            if report.questions_to_ask:
                st.markdown("#### Ask before you pay")
                for q in report.questions_to_ask[:6]:
                    st.markdown(f"- {q}")

            if report.guardrail_notes:
                st.markdown("#### Safety note")
                for n in report.guardrail_notes:
                    st.warning(n)

            with st.expander("Technical JSON (for judges/devs)"):
                st.json(json.loads(json.dumps(report.model_dump(), default=str)))

elif page == "Tenant stories":
    st.markdown("Anonymous posts — **not verified facts**. Search after running `seed_demo_data.py`.")

    loc_f = st.text_input("Locality", value="Koramangala")
    cat_f = st.text_input("Category (optional)", value="")
    sent_f = st.selectbox("Sentiment", ["", "positive", "neutral", "negative"])

    if st.button("Search", type="primary") or loc_f:
        res = search_anonymous_experiences(
            locality=loc_f or None,
            category=cat_f or None,
            sentiment=sent_f or None,
        )
        st.caption(" · ".join(res["limitations"]))
        if not res["items"]:
            st.warning("No posts. Click **Load demo database** in the sidebar, then search Koramangala.")
        for item in res["items"]:
            with st.container(border=True):
                st.markdown(f"**{item['locality']}** · {item['category']} · _{item['sentiment']}_")
                st.write(item["experience_text"])

    st.divider()
    st.markdown("#### Share your experience (no name, no phone in text)")
    with st.form("exp_form", border=True):
        eloc = st.text_input("Locality", "HSR Layout")
        eptype = st.text_input("Property type", "apartment")
        ecat = st.selectbox(
            "Category",
            [
                "Deposit and refund",
                "Maintenance",
                "Communication",
                "Agreement clarity",
                "Move-out experience",
                "General rental experience",
            ],
        )
        esent = st.selectbox("Sentiment", ["positive", "neutral", "negative"])
        etext = st.text_area("Story (min 20 characters)", height=100)
        if st.form_submit_button("Submit anonymously"):
            try:
                data = AnonymousExperienceInput(
                    locality=eloc,
                    property_type=eptype,
                    category=ecat,
                    sentiment=esent,
                    experience_text=etext,
                )
                out = create_anonymous_experience(data)
                if out["success"]:
                    st.success(f"Published status: **{out['moderation_status']}**")
                    st.warning("Save this **edit token** privately (not shown in search):")
                    st.code(out["edit_token"])
                else:
                    st.error(out.get("message", "Rejected"))
            except Exception as exc:
                st.error(str(exc))

elif page == "Rooms vacating soon":
    st.markdown("Tenant-shared leads — contact is **not** shown publicly in this MVP.")

    vloc = st.text_input("Search locality", value="Whitefield")
    rooms = search_available_rooms(locality=vloc or None)
    if not rooms["items"]:
        st.warning("No active rooms. Sidebar → **Load demo database**, then search **Whitefield**.")
    for r in rooms["items"]:
        with st.container(border=True):
            st.markdown(f"**{r['locality']}** · {r['room_type']} · **₹{r['monthly_rent_inr']:,}/mo**")
            st.write(r["description"])
            st.caption(f"From {r['availability_date']} · {r['post_kind'].replace('_', ' ')}")

    st.divider()
    st.markdown("#### I'm vacating — post availability")
    with st.form("vac_form", border=True):
        vloc2 = st.text_input("Locality", "HSR Layout")
        vrent = st.number_input("Monthly rent (₹)", min_value=1000, value=18000, step=500)
        vdate = st.date_input("Available from", date.today() + timedelta(days=14))
        vdesc = st.text_area("Description (no phone/email here)", height=80)
        vkind = st.selectbox(
            "Type",
            [
                ("room_takeover", "Room takeover"),
                ("roommate_replacement", "Roommate replacement"),
                ("availability_lead", "General availability"),
            ],
            format_func=lambda x: x[1],
        )
        vack = st.checkbox("I will check my rental agreement / owner permission")
        if st.form_submit_button("Publish listing"):
            if len(vdesc.strip()) < 15:
                st.error("Description too short.")
            else:
                out = create_vacating_post(
                    VacatingPostInput(
                        locality=vloc2,
                        property_type="apartment",
                        room_type="private room",
                        monthly_rent_inr=int(vrent),
                        availability_date=vdate,
                        post_kind=vkind[0],
                        description=vdesc,
                        contact_method="poster-shares-after-match",
                        owner_permission_ack=vack,
                    ),
                    publish=True,
                )
                if out["success"]:
                    st.success(f"Live status: **{out['status']}**")
                    st.code(out["edit_token"])
                else:
                    st.error(out.get("message", "Failed"))

elif page == "Before you sign":
    st.markdown("Checklist — not legal advice. Confirm with authorities or a lawyer.")
    for item in build_rental_checklist():
        with st.expander(item.title):
            st.write(item.description)
            st.caption(f"Type: {item.category}")
            if item.source_url:
                st.markdown(f"[Source]({item.source_url})")
    st.subheader("Reference links")
    for ref in get_karnataka_rental_guidance():
        st.markdown(f"- [{ref.title}]({ref.url}) — checked {ref.date_checked}")

else:
    st.markdown(
        """
        **What this is:** Hackathon demo for Bengaluru renters — ADK agent + tools in the repo.

        **What this is NOT:** Verified listings, legal advice, or Google/Karnataka government product.

        **Privacy:** Community posts don't ask your real name. Don't paste phone/email in stories.

        **AI chat (optional):** Set `GOOGLE_API_KEY` and run `adk web adk_agent` from `agents/rentrakshak` for conversational mode.
        This Streamlit app uses the **same risk engine** without calling Gemini.
        """
    )
