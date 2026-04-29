import streamlit as st
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import AgenticSystem

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mumzworld AI Copilot",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp { background: #0f1117; }
section[data-testid="stSidebar"] { background: #16181f !important; border-right: 1px solid #2a2d3a; }
.block-container { padding: 2rem 2.5rem 2rem 2.5rem; max-width: 1200px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Header Banner ── */
.mw-header {
    background: linear-gradient(135deg, #ff4d6d 0%, #c9184a 50%, #a4133c 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(255, 77, 109, 0.25);
}
.mw-header-title { font-size: 2rem; font-weight: 700; color: white; margin: 0; }
.mw-header-sub { font-size: 0.95rem; color: rgba(255,255,255,0.8); margin-top: 4px; }
.mw-badge {
    background: rgba(255,255,255,0.2);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
}

/* ── Query Input ── */
.stTextInput input {
    background: #1e2130 !important;
    border: 1.5px solid #2a2d3a !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    font-size: 1rem !important;
    padding: 14px 18px !important;
    transition: border-color 0.2s;
}
.stTextInput input:focus {
    border-color: #ff4d6d !important;
    box-shadow: 0 0 0 3px rgba(255, 77, 109, 0.15) !important;
}
.stTextInput label { color: #8b8fa8 !important; font-size: 0.85rem !important; font-weight: 500 !important; }

/* ── Route Badge ── */
.route-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.route-gift { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
.route-support { background: rgba(99, 179, 237, 0.15); color: #63b3ed; border: 1px solid rgba(99, 179, 237, 0.3); }

/* ── Response Cards ── */
.response-card {
    background: #1e2130;
    border: 1px solid #2a2d3a;
    border-radius: 14px;
    padding: 22px 24px;
    min-height: 120px;
    position: relative;
    overflow: hidden;
}
.response-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.response-card-en::before { background: linear-gradient(90deg, #4f8ef7, #7c3aed); }
.response-card-ar::before { background: linear-gradient(90deg, #ff4d6d, #f97316); }
.response-card-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6b7280;
    margin-bottom: 10px;
}
.response-card-text {
    color: #d1d5db;
    font-size: 0.97rem;
    line-height: 1.7;
}
.response-card-ar-text {
    direction: rtl;
    text-align: right;
    color: #d1d5db;
    font-size: 1rem;
    line-height: 1.8;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

/* ── Confidence Bar ── */
.conf-bar-wrap { margin: 16px 0; }
.conf-label { font-size: 0.78rem; color: #6b7280; margin-bottom: 6px; display: flex; justify-content: space-between; }
.conf-bar-bg { background: #2a2d3a; border-radius: 8px; height: 6px; overflow: hidden; }
.conf-bar-fill { height: 100%; border-radius: 8px; transition: width 0.6s ease; }

/* ── Product Cards ── */
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-top: 16px; }
.product-card {
    background: #1e2130;
    border: 1px solid #2a2d3a;
    border-radius: 14px;
    padding: 20px;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.product-card:hover { transform: translateY(-3px); border-color: #ff4d6d; box-shadow: 0 8px 24px rgba(255,77,109,0.12); }
.product-category {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #fb923c;
    background: rgba(251, 146, 60, 0.1);
    padding: 3px 10px;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 10px;
}
.product-name { font-size: 0.97rem; font-weight: 600; color: #e8eaf0; margin-bottom: 8px; line-height: 1.4; }
.product-price { font-size: 1.1rem; font-weight: 700; color: #ff4d6d; margin-bottom: 10px; }
.product-reason { font-size: 0.82rem; color: #6b7280; line-height: 1.5; border-top: 1px solid #2a2d3a; padding-top: 10px; }

/* ── Escalation Banner ── */
.escalation-banner {
    background: rgba(245, 101, 101, 0.1);
    border: 1px solid rgba(245, 101, 101, 0.3);
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #fc8181;
    font-size: 0.9rem;
    font-weight: 500;
    margin-top: 16px;
}

/* ── Example Chips ── */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.chip {
    background: #1e2130;
    border: 1px solid #2a2d3a;
    color: #8b8fa8;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
}
.chip:hover { background: #2a2d3a; color: #e8eaf0; border-color: #ff4d6d; }

/* ── Sidebar ── */
.sidebar-stat {
    background: #1e2130;
    border: 1px solid #2a2d3a;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.stat-label { font-size: 0.8rem; color: #6b7280; }
.stat-value { font-size: 0.85rem; font-weight: 600; color: #e8eaf0; }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; background: #48bb78; display: inline-block; margin-right: 6px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Spinner override ── */
.stSpinner > div { border-top-color: #ff4d6d !important; }

/* ── Section title ── */
.section-title {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6b7280;
    margin: 28px 0 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after { content: ''; flex: 1; height: 1px; background: #2a2d3a; }

/* ── JSON expander ── */
.streamlit-expanderHeader {
    background: #1e2130 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 10px !important;
    color: #8b8fa8 !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Load System ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_system():
    return AgenticSystem()

with st.spinner("Initializing AI system..."):
    system = get_system()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System")
    st.markdown("---")

    chroma_count = system.retrieval.collection.count()
    db_count     = len(system.db.get_all_products())

    st.markdown(f"""
    <div class="sidebar-stat">
        <span class="stat-label">🗄️ Product Database</span>
        <span class="stat-value"><span class="stat-dot"></span>{db_count} items</span>
    </div>
    <div class="sidebar-stat">
        <span class="stat-label">🔍 Vector Index</span>
        <span class="stat-value"><span class="stat-dot"></span>{chroma_count} vectors</span>
    </div>
    <div class="sidebar-stat">
        <span class="stat-label">🤖 LLM Engine</span>
        <span class="stat-value">Llama 3.3 70B</span>
    </div>
    <div class="sidebar-stat">
        <span class="stat-label">⚡ Provider</span>
        <span class="stat-value">Groq</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Re-sync Vector Index", use_container_width=True):
        with st.spinner("Syncing..."):
            system.retrieval.sync()
        st.success("✅ Sync complete!")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.75rem; color:#4b5563; line-height:1.6;">
    <b style="color:#6b7280;">Capabilities</b><br>
    🎁 Gift Finder (EN + AR)<br>
    🎧 Customer Support Triage<br>
    🔍 Semantic Product Search<br>
    🚨 Auto Human Escalation<br>
    📊 Structured JSON Output
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="mw-header">
    <div>
        <div class="mw-header-title">👶 Mumzworld AI Copilot</div>
        <div class="mw-header-sub">Intelligent Gift Finder & Customer Support — English + Arabic</div>
    </div>
    <div>
        <span class="mw-badge">🟢 Live</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Example Queries ───────────────────────────────────────────────────────────
EXAMPLES = [
    "Gift for a newborn girl under 150 AED",
    "Diapers for 6 month old baby",
    "أريد هدية لطفل عمره سنة",
    "Where is my order #4521?",
    "I want a refund for my stroller",
    "هل يمكنني استرجاع المنتج؟",
]

st.markdown('<div class="section-title">Try an example</div>', unsafe_allow_html=True)
st.markdown('<div class="chip-row">' + ''.join(
    f'<span class="chip">{q}</span>' for q in EXAMPLES
) + '</div>', unsafe_allow_html=True)


# ── Query Input ───────────────────────────────────────────────────────────────
query = st.text_input(
    "Your message",
    placeholder="e.g.  Gift for a 1 year old girl under 200 AED  ·  Where is my order?  ·  أريد هدية للأم الجديدة",
    label_visibility="collapsed",
)


# ── Process & Render ──────────────────────────────────────────────────────────
if query:
    with st.spinner("Thinking..."):
        response = system.handle_query(query)

    out = response.output

    # Route badge
    if response.route == "gift_finder":
        st.markdown('<div><span class="route-badge route-gift">🎁 Gift Finder</span></div>', unsafe_allow_html=True)
    else:
        intent_label = out.get("intent", "support").replace("_", " ").title()
        st.markdown(f'<div><span class="route-badge route-support">🎧 Support · {intent_label}</span></div>', unsafe_allow_html=True)

    # ── Confidence bar
    conf = out.get("confidence", 0)
    conf_pct = int(conf * 100)
    if conf >= 0.75:
        bar_color = "#48bb78"
    elif conf >= 0.5:
        bar_color = "#f6ad55"
    else:
        bar_color = "#fc8181"

    st.markdown(f"""
    <div class="conf-bar-wrap">
        <div class="conf-label"><span>Confidence</span><span>{conf_pct}%</span></div>
        <div class="conf-bar-bg">
            <div class="conf-bar-fill" style="width:{conf_pct}%; background:{bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bilingual responses
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown(f"""
        <div class="response-card response-card-en">
            <div class="response-card-label">🇬🇧 English Response</div>
            <div class="response-card-text">{response.response_en}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="response-card response-card-ar">
            <div class="response-card-label">🇦🇪 Arabic Response</div>
            <div class="response-card-ar-text">{response.response_ar}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Product cards (gift finder)
    if response.route == "gift_finder":
        recs = out.get("recommendations", [])
        if recs:
            st.markdown('<div class="section-title">🎁 Recommended Products</div>', unsafe_allow_html=True)
            cards_html = '<div class="product-grid">'
            for rec in recs:
                name     = rec.get("name", "")
                price    = rec.get("price_aed", "")
                category = rec.get("category", "")
                reason   = rec.get("reason", "")
                cards_html += f"""
                <div class="product-card">
                    <div class="product-category">{category}</div>
                    <div class="product-name">{name}</div>
                    <div class="product-price">💰 {price} AED</div>
                    <div class="product-reason">{reason}</div>
                </div>"""
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)

    # ── Support: extra metadata
    if response.route == "support":
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Intent", out.get("intent", "-").replace("_", " ").title())
        with col_b:
            urgency = out.get("urgency", "-").title()
            st.metric("Urgency", urgency)
        with col_c:
            st.metric("Human Needed", "Yes" if out.get("needs_human") else "No")

        if out.get("needs_human"):
            st.markdown("""
            <div class="escalation-banner">
                🚨 <span>This request has been flagged for <strong>human agent review</strong>. A team member will follow up shortly.</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Raw JSON
    with st.expander("🔍 View system output (JSON)", expanded=False):
        st.json(out)
