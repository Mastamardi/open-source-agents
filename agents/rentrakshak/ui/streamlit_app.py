"""RentRakshak Streamlit demo UI."""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rentrakshak.db.database import init_db
from rentrakshak.guardrails.content_safety import escape_html
from rentrakshak.models.schemas import AnonymousExperienceInput, VacatingPostInput
from rentrakshak.services.checklist import build_rental_checklist, get_karnataka_rental_guidance
from rentrakshak.services.community import (
    create_anonymous_experience,
    report_community_content,
    search_anonymous_experiences,
)
from rentrakshak.services.safety_report import generate_rental_safety_report
from rentrakshak.services.vacating import (
    create_vacating_post,
    search_available_rooms,
    update_vacating_post_status,
)

st.set_page_config(page_title="RentRakshak", page_icon="🏠", layout="wide")
init_db()

st.title("RentRakshak")
st.caption("Rent smarter. Stay safer. Help the next tenant.")
st.warning("Before you pay a deposit, check the risks. Nothing here verifies owners or listings.")

tab_home, tab_analyze, tab_community, tab_vacate, tab_checklist, tab_about = st.tabs(
    ["Home", "Analyze listing", "Tenant experiences", "Vacating / rooms", "Karnataka checklist", "About"]
)

with tab_home:
    st.markdown(
        """
        **RentRakshak** combines an AI rental safety agent (Google ADK) with:
        - Evidence-based red-flag checks
        - Transparent Bengaluru rent comparables (demo dataset)
        - Anonymous tenant experiences
        - Vacating tenant availability board
        """
    )
    st.info("Use **Analyze listing** for deterministic safety reports without an API key.")

with tab_analyze:
    listing = st.text_area("Listing text", height=160)
    chat = st.text_area("Landlord/broker chat (optional)", height=120)
    locality = st.text_input("Locality hint (optional)")
    if st.button("Generate safety report", type="primary"):
        if not listing.strip():
            st.error("Paste a listing first.")
        else:
            report = generate_rental_safety_report(listing, chat or None, locality_hint=locality or None)
            st.subheader(f"Risk: {report.risk_category.value}")
            st.write(report.risk_reasoning)
            if report.findings:
                for f in report.findings:
                    st.markdown(f"**{f.rule_id}** ({f.severity.value}): {f.explanation}")
                    st.caption(f"Evidence: {escape_html(f.evidence_excerpt)}")
            if report.rent_estimate:
                re = report.rent_estimate
                if re.sufficient_data:
                    st.success(
                        f"Rent range (demo data): ₹{re.rent_min_inr} – ₹{re.rent_max_inr} "
                        f"(median ₹{re.rent_median_inr}, n={re.comparable_count})"
                    )
                else:
                    st.warning("Insufficient rent comparables — no market estimate shown.")
                for lim in re.limitations:
                    st.caption(lim)
            with st.expander("Full JSON report"):
                st.json(json.loads(json.dumps(report.model_dump(), default=str)))

with tab_community:
    st.subheader("Browse experiences")
    col1, col2, col3 = st.columns(3)
    with col1:
        loc_f = st.text_input("Filter locality")
    with col2:
        cat_f = st.text_input("Filter category")
    with col3:
        sent_f = st.selectbox("Sentiment", ["", "positive", "neutral", "negative"])
    if st.button("Search experiences"):
        res = search_anonymous_experiences(
            locality=loc_f or None,
            category=cat_f or None,
            sentiment=sent_f or None,
        )
        st.caption("; ".join(res["limitations"]))
        for item in res["items"]:
            st.markdown(f"**{item['locality']}** · {item['category']} · {item['sentiment']}")
            st.write(item["experience_text"])
            st.divider()

    st.subheader("Submit anonymous experience")
    with st.form("exp_form"):
        eloc = st.text_input("Locality", "Koramangala")
        eptype = st.text_input("Property type", "apartment")
        ecat = st.text_input("Category", "Maintenance")
        esent = st.selectbox("Sentiment", ["positive", "neutral", "negative"])
        etext = st.text_area("Your experience (no phone/email)", height=120)
        submitted = st.form_submit_button("Submit")
        if submitted:
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
                    st.success(f"Status: {out['moderation_status']}. Save edit token privately.")
                    st.code(out["edit_token"])
                else:
                    st.error(out.get("message", "Rejected"))
            except Exception as exc:
                st.error(str(exc))

with tab_vacate:
    st.subheader("Available rooms (tenant-shared)")
    vloc = st.text_input("Search locality", "Bellandur")
    if st.button("Search rooms"):
        rooms = search_available_rooms(locality=vloc or None)
        for r in rooms["items"]:
            st.markdown(f"**{r['locality']}** · {r['room_type']} · ₹{r['monthly_rent_inr']}/mo")
            st.write(r["description"])
            st.caption(f"Available from {r['availability_date']} · {r['post_kind']}")
            st.divider()

    st.subheader("Post vacating availability")
    with st.form("vac_form"):
        vloc2 = st.text_input("Locality ", "HSR Layout")
        vrent = st.number_input("Monthly rent (INR)", min_value=1000, value=18000)
        vdate = st.date_input("Availability date", date.today() + timedelta(days=14))
        vdesc = st.text_area("Description (no phone/email in text)")
        vkind = st.selectbox("Post kind", ["room_takeover", "roommate_replacement", "availability_lead"])
        vack = st.checkbox("I confirm I will check agreement / owner permission")
        vsub = st.form_submit_button("Publish")
        if vsub:
            out = create_vacating_post(
                VacatingPostInput(
                    locality=vloc2,
                    property_type="apartment",
                    room_type="private room",
                    monthly_rent_inr=int(vrent),
                    availability_date=vdate,
                    post_kind=vkind,
                    description=vdesc,
                    contact_method="poster-shares-after-match",
                    owner_permission_ack=vack,
                ),
                publish=True,
            )
            if out["success"]:
                st.success(f"Posted as {out['status']}")
                st.code(out["edit_token"])
            else:
                st.error(out.get("message", "Failed"))

with tab_checklist:
    for item in build_rental_checklist():
        st.markdown(f"**{item.title}** ({item.category})")
        st.write(item.description)
    st.subheader("Legal references (starting points — confirm with authorities)")
    for ref in get_karnataka_rental_guidance():
        st.markdown(f"- [{ref.title}]({ref.url}) — checked {ref.date_checked}")

with tab_about:
    st.markdown(
        """
        **Privacy:** Anonymous posts do not ask for legal name. Edit tokens are secret; do not share publicly.
        **Moderation:** PII may be redacted; abusive content rejected.
        **Google:** Uses Google ADK with Gemini when `GOOGLE_API_KEY` is set. Not affiliated with Google or Karnataka government.
        **Model Armor:** Optional; local guardrails always apply.
        """
    )
