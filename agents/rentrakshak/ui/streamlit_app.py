"""RentRakshak - Professional Bengaluru Rental Safety Dashboard."""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

# Setup paths
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

# Initialize
init_db()

st.set_page_config(
    page_title="RentRakshak",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- THEME & CSS ---
st.markdown(
    """
    <style>
    /* Force Light Mode & Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #5E17EB;
        --primary-soft: #F5F1FF;
        --text-main: #1A1A1A;
        --text-muted: #64748B;
        --bg-app: #FDFDFD;
        --card-border: #F1F5F9;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-app) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Hide Streamlit Boilerplate */
    header, footer, [data-testid="stSidebarNav"], .stDeployButton {
        display: none !important;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid var(--card-border) !important;
        min-width: 280px !important;
    }

    .nav-item {
        padding: 12px 16px;
        margin: 4px 16px;
        border-radius: 12px;
        color: var(--text-muted);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-item-active {
        background-color: var(--primary-soft);
        color: var(--primary);
    }

    /* Hero Section */
    .hero-box {
        background: linear-gradient(105deg, #F9F7FF 0%, #FFFFFF 100%);
        border: 1px solid #E9E1FF;
        border-radius: 32px;
        padding: 48px;
        position: relative;
        overflow: hidden;
        margin-bottom: 32px;
    }

    .hero-badge {
        background: white;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 700;
        color: var(--primary);
        box-shadow: 0 2px 10px rgba(94, 23, 235, 0.08);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 20px;
    }

    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }

    .f-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        transition: transform 0.2s;
    }

    .f-card:hover {
        transform: translateY(-4px);
        border-color: var(--primary);
    }

    /* Main Dashboard container */
    .dashboard-shell {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px;
    }

    /* Professional Input Boxes */
    div[data-testid="stTextArea"] textarea {
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        background-color: #FAFAFA !important;
        padding: 16px !important;
    }

    /* Custom Purple Button */
    .stButton > button {
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(94, 23, 235, 0.2) !important;
    }

    .stButton > button:hover {
        background-color: #4C11D0 !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Brand
    st.markdown(
        """
        <div style="padding: 0 24px; margin-bottom: 40px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: #5E17EB; width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px;">🛡️</div>
                <div>
                    <h2 style="margin:0; font-size: 20px; font-weight: 800; color: #1A1A1A;">RentRakshak</h2>
                    <p style="margin:0; font-size: 12px; color: #64748B; font-weight: 500;">Namma Bengaluru. Safe Rentals.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Nav
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("✨ Analyze Listing", use_container_width=True): st.session_state.page = "Analyze"
    if st.button("👥 Community", use_container_width=True): st.session_state.page = "Community"
    if st.button("📊 Rent Estimates", use_container_width=True): st.session_state.page = "Estimates"
    if st.button("📋 Checklist", use_container_width=True): st.session_state.page = "Checklist"

    st.markdown(
        """
        <div style="position: absolute; bottom: 40px; left: 24px; right: 24px;">
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 20px;">
                <p style="margin:0; font-weight: 700; color: #1A1A1A; font-size: 14px;">ನಮ್ಮ ಬೆಂಗಳೂರು</p>
                <p style="margin:0; font-size: 12px; color: #64748B; margin-top: 4px;">Better Rentals for a Better City</p>
                <div style="height: 60px; background: #EEE; border-radius: 12px; margin-top: 12px; display: flex; align-items: center; justify-content: center; font-size: 30px; opacity: 0.5;">🏛️🚇</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- MAIN CONTENT ---
main_c, right_c = st.columns([3, 1.1], gap="large")

with main_c:
    # Header row
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px;">
            <div style="position: relative; width: 500px;">
                <input type="text" placeholder="Search localities or ask RentRakshak..." style="width:100%; padding: 14px 20px; border-radius: 16px; border: 1px solid #E2E8F0; background: white; font-size: 14px;">
            </div>
            <div style="display: flex; gap: 12px;">
                <div style="background:white; border: 1px solid #E2E8F0; padding: 10px 18px; border-radius: 14px; font-size: 14px; font-weight: 600;">📍 Bengaluru</div>
                <div style="background:white; border: 1px solid #E2E8F0; padding: 10px; border-radius: 14px; width: 44px; display: flex; align-items: center; justify-content: center;">🔔</div>
                <div style="background:#5E17EB; color: white; border-radius: 14px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-weight: 800;">O</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.page == "Home" or st.session_state.page == "Analyze":
        # Hero
        st.markdown(
            """
            <div class="hero-box">
                <div class="hero-badge">🛡️ Your Rental Safety Companion for Bengaluru</div>
                <h1 style="font-size: 44px; font-weight: 800; color: #1A1A1A; margin-bottom: 16px; line-height: 1.1;">
                    Before you pay that deposit,<br>talk to <span style="color: #5E17EB;">RentRakshak.</span>
                </h1>
                <p style="font-size: 18px; color: #64748B; margin-bottom: 32px; max-width: 600px;">
                    Check rental red flags, understand local rents, and learn from Bengaluru's tenant community.
                </p>
                <div style="display: flex; gap: 16px;">
                    <div style="background: #5E17EB; color: white; padding: 14px 28px; border-radius: 14px; font-weight: 700; cursor: pointer;">Analyze a Listing →</div>
                    <div style="background: white; border: 1px solid #E2E8F0; color: #1A1A1A; padding: 14px 28px; border-radius: 14px; font-weight: 700; cursor: pointer;">Explore Community</div>
                </div>
                <!-- Visual Decoration (Abstract Metro Train) -->
                <div style="position: absolute; right: -40px; bottom: 0; width: 340px; height: 160px; background: #5E17EB; border-radius: 40px 0 0 40px; opacity: 0.1;"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Feature Grid
        st.markdown(
            """
            <div class="feature-grid">
                <div class="f-card"><p style="font-size: 20px; margin:0 0 8px 0;">🔍</p><p style="font-weight:700; font-size:14px; margin:0;">Analyze Listings</p><p style="font-size:11px; color:#64748B; margin:0;">Detect red flags</p></div>
                <div class="f-card"><p style="font-size: 20px; margin:0 0 8px 0;">📈</p><p style="font-weight:700; font-size:14px; margin:0;">Rent Estimates</p><p style="font-size:11px; color:#64748B; margin:0;">Fair benchmarks</p></div>
                <div class="f-card"><p style="font-size: 20px; margin:0 0 8px 0;">📋</p><p style="font-weight:700; font-size:14px; margin:0;">Checklist</p><p style="font-size:11px; color:#64748B; margin:0;">Karnataka rules</p></div>
                <div class="f-card"><p style="font-size: 20px; margin:0 0 8px 0;">👥</p><p style="font-weight:700; font-size:14px; margin:0;">Community</p><p style="font-size:11px; color:#64748B; margin:0;">Tenant stories</p></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Analysis Workspace
        st.markdown("<h3 style='font-size: 20px; font-weight: 800; margin-bottom: 24px;'>✨ Analyze a Rental Listing</h3>", unsafe_allow_html=True)

        with st.container():
            tabs = st.tabs(["📄 Listing Details", "💬 Landlord Chat", "🏢 Property Details"])
            with tabs[0]:
                listing = st.text_area("Description", height=180, placeholder="Paste NoBroker/WhatsApp text here...", label_visibility="collapsed")
            with tabs[1]:
                chat = st.text_area("Chat", height=180, placeholder="Paste snippets from broker chat...", label_visibility="collapsed")
            with tabs[2]:
                locality = st.text_input("Locality Hint", placeholder="e.g. HSR Layout")

            col_btn, col_info = st.columns([1, 1.5])
            with col_btn:
                if st.button("🚀 Analyze with AI", use_container_width=True):
                    if listing.strip():
                        report = generate_rental_safety_report(listing, chat or None, locality_hint=locality or None)
                        st.session_state.report = report
                        st.toast("Analysis complete!")
                    else:
                        st.error("Paste a listing first.")
            with col_info:
                st.markdown("<p style='font-size: 12px; color: #64748B; margin-top: 14px;'>🛡️ Deterministic analysis using rule-based compliance engine.</p>", unsafe_allow_html=True)

        if "report" in st.session_state:
            rep = st.session_state.report
            st.markdown(f"#### Safety Report: {rep.risk_category.value.upper()}")
            st.info(rep.risk_reasoning)
            for f in rep.findings:
                with st.expander(f"🚩 {f.rule_id}"):
                    st.write(f.explanation)
                    st.caption(f"Evidence: {f.evidence_excerpt}")

    else:
        st.markdown(f"## {st.session_state.page}")
        st.info("Feature view coming soon...")

with right_c:
    st.markdown("<br><br>", unsafe_allow_html=True)
    # AI Assistant
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 24px; padding: 24px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">🤖</span>
                    <span style="font-weight: 800; font-size: 14px;">Ask RentRakshak</span>
                </div>
                <span style="font-size: 10px; font-weight: 700; background: #F0FDF4; color: #166534; padding: 4px 8px; border-radius: 6px;">AI ASSISTANT</span>
            </div>
            <div style="background: #F8FAFC; border-radius: 12px; padding: 14px; margin-bottom: 16px;">
                <p style="font-size: 12px; color: #1E293B; line-height: 1.5; margin:0;">
                    Hi! I'm RentRakshak 👋 Ask me anything about rentals in Bengaluru — red flags, rent estimates, or legal rights.
                </p>
            </div>
            <div style="position: relative;">
                <input type="text" placeholder="Ask a question..." style="width:100%; padding: 10px 40px 10px 14px; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 12px;">
                <div style="position: absolute; right: 8px; top: 6px; background: #5E17EB; width: 24px; height: 24px; border-radius: 6px; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px;">→</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Experiences
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 24px; padding: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span style="font-weight: 800; font-size: 14px;">Recent Stories</span>
                <span style="font-size: 11px; color: #5E17EB; font-weight: 700; cursor: pointer;">View all</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <div style="border-left: 2px solid #10B981; padding-left: 12px;">
                    <p style="margin:0; font-size: 10px; font-weight: 700; color: #10B981;">POSITIVE · Koramangala</p>
                    <p style="margin:4px 0; font-size: 12px; font-weight: 700; color: #1A1A1A;">Smooth deposit refund</p>
                    <p style="margin:0; font-size: 10px; color: #64748B;">2 days ago</p>
                </div>
                <div style="border-left: 2px solid #EF4444; padding-left: 12px;">
                    <p style="margin:0; font-size: 10px; font-weight: 700; color: #EF4444;">NEGATIVE · HSR Layout</p>
                    <p style="margin:4px 0; font-size: 12px; font-weight: 700; color: #1A1A1A;">Unnecessary deductions</p>
                    <p style="margin:0; font-size: 10px; color: #64748B;">4 days ago</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
