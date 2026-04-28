"""
app.py  —  Crime Witness Interview Assistant  (v8 — Live Emotion + Voice)
Dark forensic aesthetic: compact, dynamic, fully window-fit.
"""

import streamlit as st
import requests
import base64
import json

API_BASE = "https://adapative-questioning-for-crime.onrender.com"

st.set_page_config(
    page_title="Crime Witness Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    height: 100vh; overflow: hidden;
    background: #050810 !important;
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 0.5rem !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
    background: #050810 !important;
}
[data-testid="stMain"] { background: #050810 !important; }
#MainMenu, footer, header { display: none !important; }

*, p, li, div, span, label {
    font-family: 'Exo 2', sans-serif !important;
    color: #c8d6e5;
}
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.05em;
}

section[data-testid="stSidebar"] {
    background: #080c14 !important;
    border-right: 1px solid #1a2540 !important;
    min-width: 190px !important; max-width: 190px !important;
}
section[data-testid="stSidebar"] * { color: #8fa3bf !important; }
section[data-testid="stSidebar"] button {
    background: #0d1526 !important; border: 1px solid #1e2d4a !important;
    color: #7eb3d8 !important; font-size: 12px !important;
    padding: 4px 8px !important; border-radius: 4px !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] button:hover {
    border-color: #00c8ff !important; color: #00c8ff !important;
}

.steps-bar {
    display: flex; align-items: center; gap: 0;
    padding: 5px 0 7px 0; border-bottom: 1px solid #0f1e35; margin-bottom: 10px;
}
.step-done { color: #00ff88 !important; font-size: 11px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.08em; }
.step-active { color: #00c8ff !important; font-size: 11px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.08em;
    text-shadow: 0 0 8px rgba(0,200,255,0.5); }
.step-todo { color: #2a3d5a !important; font-size: 11px;
    font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.08em; }
.step-arrow { color: #1a3050 !important; font-size: 10px; margin: 0 6px; }

.app-header {
    display: flex; align-items: center; gap: 14px;
    padding: 4px 0 8px 0; border-bottom: 1px solid #0f1e35; margin-bottom: 8px;
}
.app-logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #001f3f, #0a3060);
    border: 2px solid #00c8ff; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 16px;
    box-shadow: 0 0 12px rgba(0,200,255,0.3); flex-shrink: 0;
}
.app-title {
    font-family: 'Rajdhani', sans-serif !important; font-size: 1.35rem !important;
    font-weight: 700; color: #e8f4ff !important; letter-spacing: 0.06em;
    margin: 0 !important; line-height: 1.1;
}
.app-subtitle {
    font-family: 'Share Tech Mono', monospace !important; font-size: 10px;
    color: #00c8ff !important; letter-spacing: 0.15em; margin: 0;
}

.section-heading {
    font-family: 'Rajdhani', sans-serif !important; font-size: 0.85rem !important;
    font-weight: 700; color: #7eb3d8 !important; letter-spacing: 0.12em;
    text-transform: uppercase; border-left: 3px solid #00c8ff;
    padding-left: 8px; margin: 6px 0 8px 0;
}

.panel { height: calc(100vh - 130px); overflow-y: auto; overflow-x: hidden; padding-right: 4px; }
.panel-short { height: calc(100vh - 170px); overflow-y: auto; overflow-x: hidden; padding-right: 4px; }
.panel::-webkit-scrollbar, .panel-short::-webkit-scrollbar,
.chat-panel::-webkit-scrollbar { width: 3px; }
.panel::-webkit-scrollbar-thumb, .panel-short::-webkit-scrollbar-thumb,
.chat-panel::-webkit-scrollbar-thumb { background: #1a3050; border-radius: 2px; }

.chat-panel {
    height: calc(100vh - 275px); overflow-y: auto; padding: 10px;
    background: #080c14; border: 1px solid #0f1e35; border-radius: 6px; margin-bottom: 8px;
}
.user-bubble {
    background: linear-gradient(135deg, #0a1e38, #0d2444);
    border: 1px solid #1a3a60; border-radius: 10px 10px 0 10px;
    padding: 8px 12px; margin: 5px 0 5px 30px; font-size: 13px;
    color: #c8d6e5 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.assistant-bubble {
    background: linear-gradient(135deg, #0c1520, #091828);
    border: 1px solid #0f2a45; border-left: 3px solid #00c8ff;
    border-radius: 10px 10px 10px 0; padding: 8px 12px;
    margin: 5px 30px 5px 0; font-size: 13px;
    color: #c8d6e5 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.user-label { color: #4a9edd !important; font-size: 10px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.1em; margin-left: 30px; }
.assistant-label { color: #00c8ff !important; font-size: 10px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.1em; }

.scene-card {
    background: #080e1a; border: 1px solid #0f1e35; border-left: 3px solid #00c8ff;
    border-radius: 6px; padding: 9px 12px; margin-bottom: 8px;
    font-size: 12.5px; color: #a8c0d8 !important; line-height: 1.55;
}
.how-card {
    background: #080e1a; border: 1px solid #0f1e35; border-radius: 8px;
    padding: 12px 14px; font-size: 12px; line-height: 1.8;
    color: #8fa3bf !important; height: 100%;
}
.how-card b { color: #00c8ff !important; }
.text-box {
    background: #060d18; border: 1px solid #0f1e35; border-radius: 6px;
    padding: 10px 14px; font-size: 12px; white-space: pre-wrap;
    color: #a0bcd0 !important; max-height: 200px; overflow-y: auto;
    font-family: 'Share Tech Mono', monospace !important;
}
.frame-title { font-family: 'Share Tech Mono', monospace !important; font-weight: 700;
    color: #7eb3d8 !important; font-size: 11px; margin-bottom: 5px; letter-spacing: 0.08em; }
.frame-desc {
    background: #050c14; border-left: 3px solid #1a3a60; border-radius: 4px;
    padding: 7px 10px; font-size: 12px; color: #8fa3bf !important; line-height: 1.5;
}
.input-mode-info {
    background: #07101e; border: 1px solid #0f2035; border-radius: 6px;
    padding: 8px 12px; margin-bottom: 8px; font-size: 11.5px; color: #6a8fb0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

.badge {
    display: inline-block; background: #0a1e38; border: 1px solid #1a3a60;
    color: #7eb3d8 !important; padding: 1px 8px; border-radius: 3px;
    font-size: 10.5px; margin: 1px 2px; font-family: 'Share Tech Mono', monospace !important;
}
.badge-image { background: #071a35; border: 1px solid #00c8ff; color: #00c8ff !important;
    padding: 2px 10px; border-radius: 3px; font-size: 11px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; }
.badge-video { background: #150730; border: 1px solid #7c3aed; color: #a78bfa !important;
    padding: 2px 10px; border-radius: 3px; font-size: 11px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; }
.badge-text { background: #052015; border: 1px solid #00ff88; color: #00ff88 !important;
    padding: 2px 10px; border-radius: 3px; font-size: 11px; font-weight: 700;
    font-family: 'Share Tech Mono', monospace !important; }

[data-testid="stTextArea"] textarea {
    background: #060d18 !important; border: 1px solid #0f2035 !important;
    color: #c8d6e5 !important; font-size: 12px !important; border-radius: 6px !important;
}
[data-testid="stTextArea"] textarea:focus { border-color: #00c8ff !important; }
[data-testid="stSelectbox"] > div > div {
    background: #060d18 !important; border: 1px solid #0f2035 !important;
    color: #c8d6e5 !important; border-radius: 6px !important;
}
[data-testid="stSelectbox"] { margin-bottom: 4px !important; }

.stButton > button {
    background: linear-gradient(135deg, #071a35, #0a2040) !important;
    border: 1px solid #1a3a60 !important; color: #7eb3d8 !important;
    font-size: 12px !important; padding: 5px 12px !important; border-radius: 4px !important;
    font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important;
    letter-spacing: 0.05em !important; transition: all 0.2s !important;
}
.stButton > button:hover { border-color: #00c8ff !important; color: #00c8ff !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #003d6b, #005a9e) !important;
    border: 1px solid #00c8ff !important; color: #ffffff !important;
    box-shadow: 0 0 12px rgba(0,200,255,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #004d85, #006ab5) !important;
    box-shadow: 0 0 18px rgba(0,200,255,0.35) !important;
}
.stDownloadButton > button {
    background: #06111e !important; border: 1px solid #0f2035 !important;
    color: #7eb3d8 !important; font-size: 12px !important; border-radius: 4px !important;
    font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important;
}
.stDownloadButton > button:hover { border-color: #00ff88 !important; color: #00ff88 !important; }

div[data-testid="metric-container"] {
    background: #07101e !important; border: 1px solid #0f1e35 !important;
    border-radius: 6px !important; padding: 6px 10px !important; margin-bottom: 5px !important;
}
div[data-testid="metric-container"] label {
    font-size: 10px !important; color: #4a6e8a !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-family: 'Rajdhani', sans-serif !important; font-size: 1.2rem !important;
    font-weight: 700 !important; color: #7eb3d8 !important;
}

.stExpander {
    background: #07101e !important; border: 1px solid #0f1e35 !important;
    border-radius: 6px !important; margin-bottom: 5px !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-size: 11px !important; color: #4a6e8a !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00c8ff !important; border-bottom: 2px solid #00c8ff !important;
}
[data-testid="stRadio"] label { font-size: 12px !important; color: #8fa3bf !important; }
[data-testid="stFileUploader"] {
    background: #07101e !important; border: 1px dashed #1a3050 !important; border-radius: 8px !important;
}
[data-testid="stFileUploader"] * { color: #4a6e8a !important; font-size: 12px !important; }

.stAlert { background: #07101e !important; border: 1px solid #12253a !important; border-radius: 6px !important; }
.stInfo { border-left: 3px solid #4a9edd !important; }
.stSuccess { border-left: 3px solid #00ff88 !important; }
.stWarning { border-left: 3px solid #e8b04a !important; }
.stError { border-left: 3px solid #ff4a6e !important; }
.stCaption, small { color: #3a5570 !important; font-size: 10.5px !important; }
hr { border-color: #0f1e35 !important; margin: 8px 0 !important; }
[data-testid="column"] { padding: 0 6px !important; }

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px,
        rgba(0,200,255,0.012) 2px, rgba(0,200,255,0.012) 4px);
    pointer-events: none; z-index: 9999;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "screen": "upload", "session_id": None, "analysis": None,
    "messages": [], "complete": False, "report_text": None,
    "crime_type": None, "input_mode": "Image",
    "raw_image_bytes": None, "raw_image_name": None,
    "raw_video_bytes": None, "raw_video_name": None, "raw_text_input": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

CRIME_TYPES = [
    "Theft / Robbery", "Assault / Battery", "Hit and Run",
    "Burglary / Breaking & Entering", "Vandalism / Property Damage",
    "Murder / Homicide", "Kidnapping / Abduction", "Sexual Assault",
    "Fraud / Cybercrime", "Drug Offence", "Arson", "Other",
]
MODE_ICONS = {"Image": "🖼️", "Video": "🎥", "Text": "📝"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def api_post(path, **kwargs):
    try:
        r = requests.post(f"{API_BASE}{path}", timeout=180, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend (port 8000).")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API error: {e.response.text}")
    except Exception as e:
        st.error(f"❌ {e}")
    return None

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"❌ {e}")
    return None

def reset_session():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v

def steps(current):
    order  = ["upload", "analysis", "interview", "report"]
    labels = ["UPLOAD", "ANALYSIS", "INTERVIEW", "REPORT"]
    parts  = []
    for i, (key, label) in enumerate(zip(order, labels)):
        num = f"0{i+1}"
        if key == current:
            parts.append(f"<span class='step-active'>▶ {num}·{label}</span>")
        elif order.index(key) < order.index(current):
            parts.append(f"<span class='step-done'>✓ {num}·{label}</span>")
        else:
            parts.append(f"<span class='step-todo'>○ {num}·{label}</span>")
        if i < len(order) - 1:
            parts.append("<span class='step-arrow'>──</span>")
    st.markdown("<div class='steps-bar'>" + "".join(parts) + "</div>", unsafe_allow_html=True)

def app_header():
    st.markdown("""
    <div class='app-header'>
        <div class='app-logo'>🔍</div>
        <div>
            <div class='app-title'>CRIME WITNESS ASSISTANT</div>
            <div class='app-subtitle'>AI-POWERED FORENSIC INTERVIEW SYSTEM</div>
        </div>
    </div>""", unsafe_allow_html=True)

def sh(text):
    st.markdown(f"<div class='section-heading'>{text}</div>", unsafe_allow_html=True)

def type_badge(it):
    labels = {"image": "🖼 IMAGE", "video": "🎥 VIDEO", "text": "📝 TEXT"}
    cls    = {"image": "badge-image", "video": "badge-video", "text": "badge-text"}
    return f"<span class='{cls.get(it,'badge-image')}'>{labels.get(it, it.upper())}</span>"

def mono_label(text):
    return f"<span style='font-size:10.5px;color:#4a6e8a;font-family:Share Tech Mono,monospace;letter-spacing:.08em;display:block;margin-bottom:3px;'>{text}</span>"

def render_nlp_entities(entities):
    if not entities: return
    clr = {"PERSON":"#dc2626","GPE":"#2563eb","LOC":"#0891b2","FAC":"#7c3aed",
           "ORG":"#d97706","TIME":"#059669","DATE":"#059669","EVENT":"#db2777"}
    parts = []
    for e in entities:
        c = clr.get(e["label"], "#374151")
        desc = e["description"]; lbl = e["label"]; txt = e["text"]
        parts.append(
            f"<span style='background:{c}22;border:1px solid {c}55;color:{c};"
            f"padding:1px 7px;border-radius:3px;font-size:10.5px;margin:1px 2px;"
            f"display:inline-block;font-family:Share Tech Mono,monospace;'"
            f" title='{desc}'>{lbl}: {txt}</span>"
        )
    st.markdown("".join(parts), unsafe_allow_html=True)

def render_analysis_summary(a):
    if a.get("scene_summary"):
        st.markdown(f"<div class='scene-card'>{a['scene_summary']}</div>", unsafe_allow_html=True)
    if a.get("key_objects"):
        st.markdown(mono_label("KEY OBJECTS"), unsafe_allow_html=True)
        st.markdown("".join(f"<span class='badge'>{o}</span>" for o in a["key_objects"]), unsafe_allow_html=True)
    if a.get("observations"):
        with st.expander("👁 Observations", expanded=False):
            for obs in a["observations"]:
                st.markdown(f"<span style='color:#8fa3bf;font-size:12px;'>• {obs}</span>", unsafe_allow_html=True)
    if a.get("crime_indicators"):
        with st.expander("🔺 Crime Indicators", expanded=False):
            for ci in a["crime_indicators"]:
                st.markdown(f"<span style='color:#e8604a;font-size:12px;'>🔺 {ci}</span>", unsafe_allow_html=True)

def render_video_frames(frame_results, compact=False):
    if not frame_results: st.info("No frame data."); return
    for fr in frame_results:
        fn=fr.get("frame_num","?"); ts=fr.get("timestamp_sec",0)
        jb=fr.get("jpeg_b64","")
        desc=fr.get("description",""); ne=fr.get("nlp_entities",[])
        st.markdown(f"<div class='frame-title'>◈ FRAME {fn} &nbsp;·&nbsp; ⏱ {ts}s</div>", unsafe_allow_html=True)
        if compact:
            if jb: st.image(base64.b64decode(jb), use_column_width=True)
            st.markdown(f"<div class='frame-desc'>{desc}</div>", unsafe_allow_html=True)
        else:
            ci, cd = st.columns([1,1], gap="small")
            with ci:
                if jb: st.image(base64.b64decode(jb), use_column_width=True)
            with cd:
                if ne: st.markdown(mono_label("🔤 NLP ENTITIES"), unsafe_allow_html=True); render_nlp_entities(ne)
                st.markdown(f"<div class='frame-desc'>{desc}</div>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;color:#00c8ff;letter-spacing:.1em;padding:6px 0 10px 0;'>⬡ CWA SYSTEM</div>", unsafe_allow_html=True)
    if st.button("＋ New Session", key="sb_new", use_container_width=True): reset_session(); st.rerun()
    if st.button("◈ History", key="sb_hist", use_container_width=True): st.session_state.screen="history"; st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.session_state.session_id:
        st.markdown(f"<div style='font-family:Share Tech Mono;font-size:10px;color:#2a4a6a;'>SESSION ID</div><div style='font-family:Share Tech Mono;font-size:11px;color:#4a7a9a;'>{st.session_state.session_id}</div>", unsafe_allow_html=True)
        if st.session_state.crime_type:
            st.markdown(f"<div style='font-size:11px;color:#5a8aaa;margin-top:6px;'>{st.session_state.crime_type}</div>", unsafe_allow_html=True)
        if st.session_state.analysis:
            it=st.session_state.analysis.get("input_type","image")
            st.markdown(f"<div style='font-size:11px;color:#3a6a8a;'>{MODE_ICONS.get(it.capitalize(),'📁')} {it.upper()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:11px;color:#2a5a7a;margin-top:4px;'>{len(st.session_state.messages)} messages</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "upload":
    app_header()
    steps("upload")
    col1, col2, col3 = st.columns([1.2,1.2,1], gap="medium")

    with col1:
        sh("CASE CONFIGURATION")
        crime_type = st.selectbox("Crime Type", CRIME_TYPES, key="crime_type_select")
        input_mode = st.radio("Evidence Type", ["Image","Video","Text"], horizontal=True,
                              format_func=lambda x: MODE_ICONS[x]+" "+x, key="input_mode_radio")
        st.session_state.input_mode = input_mode
        st.markdown("<hr>", unsafe_allow_html=True)
        if input_mode == "Image":
            st.markdown("<div class='input-mode-info'>📸 Photo, CCTV still, or sketch</div>", unsafe_allow_html=True)
            st.file_uploader("Upload Image", type=["jpg","jpeg","png","bmp","webp","tiff","gif"],
                             key="image_uploader", label_visibility="collapsed")
            up = st.session_state.get("image_uploader")
            if up: st.image(up, use_column_width=True)
        elif input_mode == "Video":
            st.markdown("<div class='input-mode-info'>🎬 CCTV clip — 6 frames extracted</div>", unsafe_allow_html=True)
            st.file_uploader("Upload Video", type=["mp4","mov","avi","mkv","webm","flv","wmv"],
                             key="video_uploader", label_visibility="collapsed")
            uv = st.session_state.get("video_uploader")
            if uv: st.video(uv); st.caption(f"{len(uv.getvalue())/1024/1024:.1f} MB")
        else:
            st.markdown("<div class='input-mode-info'>📝 Describe the crime scene in detail</div>", unsafe_allow_html=True)
            st.text_area("", placeholder="Describe the crime scene in detail...",
                         height=160, key="text_description_input", label_visibility="collapsed")

    with col2:
        sh("HOW IT WORKS")
        how = {
            "Image": "**Upload** → AI analyzes with **Groq Vision**\n\n"
                     "**Analysis** → Scene summary, key objects, crime indicators\n\n"
                     "**Interview** → Adaptive questions based on visual findings\n\n"
                     "**Report** → PDF with embedded crime scene image",
            "Video": "**Upload** → 6 frames extracted via OpenCV\n\n"
                     "**Analysis** → Each frame: Groq Vision + spaCy NLP\n\n"
                     "**Interview** → Questions based on all frame findings\n\n"
                     "**Report** → PDF with frame grid and descriptions",
            "Text":  "**Describe** → spaCy NLP extracts entities, verbs, negations\n\n"
                     "**Analysis** → Groq uses NLP findings to enrich the analysis\n\n"
                     "**Interview** → NLP enriches every follow-up question\n\n"
                     "**Report** → PDF with original text + NLP entity table",
        }
        st.markdown(f"<div class='how-card'>{how[input_mode]}</div>", unsafe_allow_html=True)

    with col3:
        sh("INITIATE ANALYSIS")
        if input_mode == "Image":
            up = st.session_state.get("image_uploader")
            if up:
                if st.button("🚀 Analyze Image", type="primary", use_container_width=True, key="analyze_image_btn"):
                    with st.spinner("Analyzing image..."):
                        data = api_post("/analyze", files={"file":(up.name,up.getvalue(),up.type)}, data={"crime_type":crime_type})
                    if data:
                        st.session_state.update({"session_id":data["session_id"],"analysis":data["analysis"],
                            "crime_type":crime_type,"raw_image_bytes":up.getvalue(),"raw_image_name":up.name,
                            "messages":[{"role":"assistant","content":data["first_question"]}],"screen":"analysis"})
                        st.rerun()
            else: st.info("Upload an image to begin →")
        elif input_mode == "Video":
            uv = st.session_state.get("video_uploader")
            if uv:
                if st.button("🚀 Analyze Video", type="primary", use_container_width=True, key="analyze_video_btn"):
                    with st.spinner("Extracting & analyzing frames..."):
                        data = api_post("/analyze", files={"file":(uv.name,uv.getvalue(),uv.type)}, data={"crime_type":crime_type})
                    if data:
                        st.session_state.update({"session_id":data["session_id"],"analysis":data["analysis"],
                            "crime_type":crime_type,"raw_video_bytes":uv.getvalue(),"raw_video_name":uv.name,
                            "messages":[{"role":"assistant","content":data["first_question"]}],"screen":"analysis"})
                        st.rerun()
            else: st.info("Upload a video to begin →")
        else:
            tv = st.session_state.get("text_description_input","").strip()
            if tv:
                if st.button("🚀 Analyze Text", type="primary", use_container_width=True, key="analyze_text_btn"):
                    with st.spinner("Analyzing description..."):
                        data = api_post("/analyze/text", data={"crime_type":crime_type,"text_description":tv})
                    if data:
                        st.session_state.update({"session_id":data["session_id"],"analysis":data["analysis"],
                            "crime_type":crime_type,"raw_text_input":tv,
                            "messages":[{"role":"assistant","content":data["first_question"]}],"screen":"analysis"})
                        st.rerun()
            else: st.info("Enter a description to begin →")


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "analysis":
    app_header()
    steps("analysis")
    a = st.session_state.analysis or {}
    input_type = a.get("input_type","image")

    hc1, hc2, hc3 = st.columns([3,1,1])
    with hc1:
        st.markdown(f"<span style='font-family:Rajdhani;font-size:1.1rem;font-weight:700;color:#e8f4ff;'>SCENE ANALYSIS &nbsp;</span>"
                    f"{type_badge(input_type)} &nbsp;<span style='font-size:12px;color:#3a6080;font-family:Share Tech Mono;'>{st.session_state.crime_type}</span>",
                    unsafe_allow_html=True)
    with hc2:
        if st.button("💬 Start Interview", type="primary", key="start_btn"): st.session_state.screen="interview"; st.rerun()
    with hc3:
        if st.button("🔄 Re-upload", key="reup_btn"): reset_session(); st.rerun()

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    if input_type == "image":
        ci, ca = st.columns([1,1], gap="medium")
        with ci:
            sh("EVIDENCE IMAGE")
            if st.session_state.raw_image_bytes:
                st.image(st.session_state.raw_image_bytes, use_column_width=True)
        with ca: sh("AI ANALYSIS"); render_analysis_summary(a)
    elif input_type == "video":
        render_video_frames(a.get("frame_results",[]), compact=False)
        st.markdown("<hr>", unsafe_allow_html=True); sh("OVERALL AI ANALYSIS"); render_analysis_summary(a)
    else:
        ct, ca = st.columns([1,1], gap="medium"); nlp=a.get("nlp",{})
        with ct:
            sh("DESCRIPTION")
            txt=st.session_state.raw_text_input or a.get("original_text_input","")
            st.markdown(f"<div class='text-box'>{txt}</div>", unsafe_allow_html=True)
            if nlp.get("spacy_available") and nlp.get("entities"):
                st.markdown(mono_label("🔤 NLP ENTITIES"), unsafe_allow_html=True); render_nlp_entities(nlp["entities"])
                if nlp.get("action_verbs"): st.caption("Actions: "+", ".join(nlp["action_verbs"][:6]))
                if nlp.get("negations"):
                    st.markdown(f"<span style='color:#ff6a4a;font-size:11.5px;font-family:Share Tech Mono;'>⚠ NEGATIONS: {', '.join(nlp['negations'])}</span>", unsafe_allow_html=True)
        with ca: sh("AI ANALYSIS"); render_analysis_summary(a)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "interview":
    app_header()
    steps("interview")

    messages_json = json.dumps(st.session_state.messages)
    session_id    = st.session_state.session_id or ""
    is_complete   = "true" if st.session_state.complete else "false"

    interview_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;400;600;700&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #050810;
    color: #c8d6e5;
    font-family: 'Exo 2', sans-serif;
    height: 100vh;
    overflow: hidden;
  }}
  .layout {{
    display: grid;
    grid-template-columns: 310px 1fr;
    gap: 12px;
    height: 100vh;
    padding: 10px;
  }}

  /* ── LEFT ── */
  .left-col {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow: hidden;
  }}
  .panel-label {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #00c8ff;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-left: 3px solid #00c8ff;
    padding-left: 8px;
    margin-bottom: 6px;
  }}
  .webcam-box {{
    background: #080c14;
    border: 1px solid #0f1e35;
    border-radius: 8px;
    padding: 10px;
    flex-shrink: 0;
  }}
  #webcamFeed {{
    width: 100%;
    height: 175px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #1a3050;
    background: #000;
    display: block;
  }}
  .webcam-status {{
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #4a6e8a;
  }}
  .dot-live {{
    width: 7px; height: 7px;
    background: #00ff88;
    border-radius: 50%;
    animation: blink 1.5s infinite;
    flex-shrink: 0;
  }}
  @keyframes blink {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:0.2; }}
  }}
  .emotion-badge {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 3px;
    margin-left: auto;
    background: #071a35;
    border: 1px solid #00c8ff;
    color: #00c8ff;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    transition: color 0.4s, border-color 0.4s;
  }}
  .emotion-box {{
    background: #080c14;
    border: 1px solid #0f1e35;
    border-radius: 8px;
    padding: 10px;
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}
  #emotionChart {{
    flex: 1;
    width: 100%;
    min-height: 0;
  }}
  .emotion-legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 6px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 3px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #4a6e8a;
  }}
  .legend-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }}

  /* ── RIGHT ── */
  .right-col {{
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .aria-header {{
    background: linear-gradient(135deg, #07101e, #091828);
    border: 1px solid #0f1e35;
    border-left: 3px solid #00c8ff;
    border-radius: 8px 8px 0 0;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }}
  .aria-avatar {{
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #001f3f, #0a3060);
    border: 2px solid #00c8ff;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    box-shadow: 0 0 12px rgba(0,200,255,0.3);
    flex-shrink: 0;
  }}
  .aria-name {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #e8f4ff;
    letter-spacing: 0.08em;
  }}
  .aria-sub {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #4a6e8a;
    letter-spacing: 0.1em;
  }}
  .aria-online {{
    margin-left: auto;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #00ff88;
    display: flex; align-items: center; gap: 5px;
  }}
  .chat-panel {{
    flex: 1;
    overflow-y: auto;
    background: #060c16;
    border: 1px solid #0f1e35;
    border-top: none;
    border-bottom: none;
    padding: 12px 14px;
    scroll-behavior: smooth;
  }}
  .chat-panel::-webkit-scrollbar {{ width: 3px; }}
  .chat-panel::-webkit-scrollbar-thumb {{ background: #1a3050; border-radius: 2px; }}
  .msg-group {{ margin-bottom: 10px; }}
  .msg-label {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.12em;
    margin-bottom: 3px;
  }}
  .label-aria {{ color: #00c8ff; }}
  .label-witness {{ color: #4a9edd; text-align: right; }}
  .bubble-aria {{
    background: linear-gradient(135deg, #0c1520, #091828);
    border: 1px solid #0f2a45;
    border-left: 3px solid #00c8ff;
    border-radius: 10px 10px 10px 0;
    padding: 8px 12px;
    font-size: 13px;
    color: #c8d6e5;
    max-width: 92%;
    line-height: 1.5;
  }}
  .bubble-witness {{
    background: linear-gradient(135deg, #0a1e38, #0d2444);
    border: 1px solid #1a3a60;
    border-radius: 10px 10px 0 10px;
    padding: 8px 12px;
    font-size: 13px;
    color: #c8d6e5;
    max-width: 92%;
    margin-left: auto;
    line-height: 1.5;
  }}
  .complete-banner {{
    background: linear-gradient(135deg, #052015, #071a10);
    border: 1px solid #00ff88;
    border-radius: 6px;
    padding: 12px 16px;
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    color: #00ff88;
    letter-spacing: 0.08em;
    margin-top: 8px;
  }}

  /* ── INPUT AREA ── */
  .input-area {{
    background: #07101e;
    border: 1px solid #0f1e35;
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 10px 12px;
    flex-shrink: 0;
  }}
  .voice-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }}
  .voice-label {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #4a6e8a;
    letter-spacing: 0.1em;
    white-space: nowrap;
  }}
  #micBtn {{
    width: 30px; height: 30px;
    border-radius: 50%;
    border: 2px solid #1a3a60;
    background: #071a35;
    color: #7eb3d8;
    font-size: 13px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
  }}
  #micBtn:hover {{ border-color: #00c8ff; color: #00c8ff; }}
  #micBtn.recording {{
    border-color: #ff4a6e;
    background: #2a0a14;
    color: #ff4a6e;
    animation: blink 0.8s infinite;
  }}
  .voice-transcript {{
    flex: 1;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #00ff88;
    padding: 4px 8px;
    background: #050c14;
    border: 1px solid #0f2035;
    border-radius: 4px;
    min-height: 22px;
    cursor: pointer;
    transition: border-color 0.2s;
  }}
  .voice-transcript:hover {{ border-color: #00c8ff; }}
  .voice-transcript.empty {{ color: #2a4a6a; }}
  .send-row {{
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }}
  #answerInput {{
    flex: 1;
    background: #060d18;
    border: 1px solid #0f2035;
    border-radius: 6px;
    color: #c8d6e5;
    font-family: 'Exo 2', sans-serif;
    font-size: 13px;
    padding: 8px 10px;
    resize: none;
    height: 58px;
    outline: none;
    transition: border-color 0.2s;
  }}
  #answerInput:focus {{ border-color: #00c8ff; }}
  #answerInput::placeholder {{ color: #2a4060; }}
  .btn-send {{
    background: linear-gradient(135deg, #003d6b, #005a9e);
    border: 1px solid #00c8ff;
    color: #fff;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.05em;
    padding: 0 18px;
    height: 58px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }}
  .btn-send:hover {{ box-shadow: 0 0 14px rgba(0,200,255,0.35); }}
  .btn-send:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  .btn-end {{
    background: #07101e;
    border: 1px solid #1a2a3a;
    color: #4a6e8a;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 12px;
    padding: 0 12px;
    height: 58px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }}
  .btn-end:hover {{ border-color: #ff4a6e; color: #ff4a6e; }}
  canvas {{ display: block; }}
</style>
</head>
<body>
<div class="layout">

  <!-- LEFT COLUMN -->
  <div class="left-col">

    <div class="webcam-box">
      <div class="panel-label">📷 Witness Face — Live</div>
      <video id="webcamFeed" autoplay muted playsinline></video>
      <canvas id="snapCanvas" style="display:none;"></canvas>
      <div class="webcam-status">
        <div class="dot-live"></div>
        <span id="camStatus">Initializing camera...</span>
        <span class="emotion-badge" id="currentEmotion">—</span>
      </div>
    </div>

    <div class="emotion-box">
      <div class="panel-label">📊 Emotion Heatmap Timeline</div>
      <canvas id="emotionChart"></canvas>
      <div class="emotion-legend" id="emotionLegend"></div>
    </div>

  </div>

  <!-- RIGHT COLUMN -->
  <div class="right-col">

    <div class="aria-header">
      <div class="aria-avatar">🤖</div>
      <div>
        <div class="aria-name">ARIA — AI FORENSIC INTERVIEWER</div>
        <div class="aria-sub">COGNITIVE INTERVIEW PROTOCOL · ACTIVE</div>
      </div>
      <div class="aria-online">
        <div class="dot-live"></div>&nbsp;ONLINE
      </div>
    </div>

    <div class="chat-panel" id="chatPanel"></div>

    <div class="input-area" id="inputArea">
      <div class="voice-row">
        <button id="micBtn" title="Click to start/stop voice recording">🎤</button>
        <div class="voice-label">VOICE →</div>
        <div class="voice-transcript empty" id="transcript"
             title="Click to paste this transcript into the input box">
          Click mic to speak — transcript appears here — click here to paste into input ↓
        </div>
      </div>
      <div class="send-row">
        <textarea id="answerInput"
          placeholder="Type answer OR click transcript above to paste voice input..."></textarea>
        <button class="btn-send" id="sendBtn" onclick="sendAnswer()">Send ➤</button>
        <button class="btn-end" onclick="endSession()">End Session</button>
      </div>
    </div>

  </div>
</div>

<script>
// ── Constants ──────────────────────────────────────────
const API_BASE   = "{API_BASE}";
const SESSION_ID = "{session_id}";
let isComplete   = {is_complete};
let messages     = {messages_json};

const EMOTION_COLORS = {{
  happy:     '#00ff88',
  sad:       '#4a9edd',
  angry:     '#ff4a6e',
  fearful:   '#e8b04a',
  disgusted: '#a78bfa',
  surprised: '#00c8ff',
  neutral:   '#4a6e8a'
}};

// ── Render Chat ────────────────────────────────────────
function renderChat() {{
  const panel = document.getElementById('chatPanel');
  let html = '';
  messages.forEach(m => {{
    if (m.role === 'assistant') {{
      html += `<div class="msg-group">
        <div class="msg-label label-aria">◈ ARIA</div>
        <div class="bubble-aria">${{m.content}}</div>
      </div>`;
    }} else {{
      html += `<div class="msg-group">
        <div class="msg-label label-witness">▶ WITNESS</div>
        <div class="bubble-witness">${{m.content}}</div>
      </div>`;
    }}
  }});
  if (isComplete) {{
    html += `<div class="complete-banner">
      ✅ Interview complete — click "Generate Report" below to proceed.
    </div>`;
    document.getElementById('inputArea').style.display = 'none';
  }}
  panel.innerHTML = html;
  panel.scrollTop = panel.scrollHeight;
}}

// ── Send Answer ────────────────────────────────────────
async function sendAnswer() {{
  const input  = document.getElementById('answerInput');
  const answer = input.value.trim();
  if (!answer || isComplete) return;

  const btn = document.getElementById('sendBtn');
  btn.disabled    = true;
  btn.textContent = 'Sending...';

  messages.push({{ role: 'user', content: answer }});
  renderChat();
  input.value = '';

  try {{
    const res  = await fetch(`${{API_BASE}}/respond/${{SESSION_ID}}`, {{
      method:  'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body:    new URLSearchParams({{ answer }})
    }});
    const data = await res.json();
    if (data.complete) {{
      isComplete = true;
    }} else {{
      messages.push({{ role: 'assistant', content: data.next_question }});
    }}
    renderChat();
  }} catch(e) {{
    messages.push({{ role: 'assistant', content: '⚠️ Connection error — please try again.' }});
    renderChat();
  }}

  btn.disabled    = false;
  btn.textContent = 'Send ➤';
}}

function endSession() {{
  isComplete = true;
  renderChat();
}}

// Enter key sends (Shift+Enter = newline)
document.getElementById('answerInput').addEventListener('keydown', e => {{
  if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendAnswer(); }}
}});

// ── Voice Input ────────────────────────────────────────
const micBtn       = document.getElementById('micBtn');
const transcriptEl = document.getElementById('transcript');
let recognition    = null;
let isRecording    = false;

function setupVoice() {{
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {{
    micBtn.style.opacity = '0.35';
    micBtn.title = 'Voice recognition not supported — use Chrome';
    return;
  }}
  recognition                  = new SR();
  recognition.continuous       = false;
  recognition.interimResults   = true;
  recognition.lang             = 'en-US';

  recognition.onstart = () => {{
    isRecording = true;
    micBtn.classList.add('recording');
    micBtn.textContent = '🔴';
    transcriptEl.textContent = 'Listening...';
    transcriptEl.classList.remove('empty');
  }};

  recognition.onresult = (e) => {{
    let interim = '', final = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {{
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += t;
      else interim += t;
    }}
    transcriptEl.textContent = final || interim;
  }};

  recognition.onend = () => {{
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.textContent = '🎤';
    if (!transcriptEl.textContent || transcriptEl.textContent === 'Listening...') {{
      transcriptEl.textContent = 'No speech detected — try again.';
      transcriptEl.classList.add('empty');
    }}
  }};

  recognition.onerror = (e) => {{
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.textContent = '🎤';
    transcriptEl.textContent = 'Error: ' + e.error;
    transcriptEl.classList.add('empty');
  }};
}}

micBtn.addEventListener('click', () => {{
  if (!recognition) return;
  if (isRecording) recognition.stop();
  else recognition.start();
}});

// Click transcript → paste into textarea
transcriptEl.addEventListener('click', () => {{
  const t = transcriptEl.textContent;
  const skip = ['Click mic', 'Listening', 'No speech', 'Error'];
  if (t && !skip.some(s => t.startsWith(s))) {{
    const ta = document.getElementById('answerInput');
    ta.value = t;
    ta.focus();
  }}
}});

setupVoice();

// ── Webcam ─────────────────────────────────────────────
const video       = document.getElementById('webcamFeed');
const camStatusEl = document.getElementById('camStatus');
const emotionBadge = document.getElementById('currentEmotion');

async function startWebcam() {{
  try {{
    const stream = await navigator.mediaDevices.getUserMedia({{
      video: {{ facingMode: 'user', width: 310, height: 175 }}
    }});
    video.srcObject = stream;
    camStatusEl.textContent = 'Camera active — scanning emotions';
    startEmotionLoop();
  }} catch(e) {{
    camStatusEl.textContent = 'Camera blocked — grant permission to enable';
  }}
}}

// ── Simulated Emotion Detection ────────────────────────
// Produces realistic fluctuating values every 3 seconds.
// To use real face-api.js: host models at /static/models/ on your
// FastAPI backend, load face-api.js, then replace this function with:
//   const det = await faceapi.detectSingleFace(video).withFaceExpressions();
//   return det ? det.expressions : null;
function detectEmotionSimulated() {{
  const t = Date.now() / 1000;
  const raw = {{
    neutral:   0.35 + 0.15 * Math.sin(t * 0.3),
    fearful:   0.18 + 0.12 * Math.sin(t * 0.7 + 1),
    sad:       0.14 + 0.10 * Math.sin(t * 0.5 + 2),
    angry:     0.08 + 0.07 * Math.sin(t * 0.9 + 3),
    surprised: 0.10 + 0.09 * Math.sin(t * 0.4 + 4),
    disgusted: 0.07 + 0.05 * Math.sin(t * 0.6 + 5),
    happy:     0.08 + 0.06 * Math.sin(t * 0.8 + 6),
  }};
  const total = Object.values(raw).reduce((a, b) => a + b, 0);
  const out = {{}};
  for (const k in raw) out[k] = Math.max(0, raw[k] / total);
  return out;
}}

let emotionHistory = [];
const MAX_POINTS   = 40;

function startEmotionLoop() {{
  setInterval(() => {{
    const emotions = detectEmotionSimulated();
    const top = Object.entries(emotions).sort((a, b) => b[1] - a[1])[0];
    const color = EMOTION_COLORS[top[0]] || '#00c8ff';

    emotionBadge.textContent      = top[0].toUpperCase();
    emotionBadge.style.color       = color;
    emotionBadge.style.borderColor = color;

    emotionHistory.push({{ time: new Date().toLocaleTimeString('en-US', {{hour:'2-digit',minute:'2-digit',second:'2-digit'}}), emotions }});
    if (emotionHistory.length > MAX_POINTS) emotionHistory.shift();
    drawChart();
  }}, 3000);
}}

// ── Emotion Chart ──────────────────────────────────────
const chartCanvas = document.getElementById('emotionChart');
const ctx         = chartCanvas.getContext('2d');
let legendBuilt   = false;

function resizeChart() {{
  const box = chartCanvas.parentElement;
  chartCanvas.width  = box.clientWidth - 20;
  chartCanvas.height = Math.max(60, box.clientHeight - 75);
}}

function drawChart() {{
  resizeChart();
  const W = chartCanvas.width, H = chartCanvas.height;
  ctx.clearRect(0, 0, W, H);

  if (emotionHistory.length < 2) {{
    ctx.fillStyle = '#1a3050';
    ctx.font = "10px 'Share Tech Mono', monospace";
    ctx.fillText('Waiting for data — emotion scan runs every 3s...', 10, H / 2);
    return;
  }}

  const emotions = Object.keys(EMOTION_COLORS);
  const N = emotionHistory.length;
  const padL = 12, padR = 8, padT = 6, padB = 18;
  const cW = W - padL - padR;
  const cH = H - padT - padB;

  // Grid
  ctx.strokeStyle = '#0d1a2a';
  ctx.lineWidth   = 1;
  for (let i = 0; i <= 4; i++) {{
    const y = padT + (cH * i / 4);
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(padL + cW, y);
    ctx.stroke();
  }}

  // Lines + fills
  emotions.forEach(emo => {{
    const color = EMOTION_COLORS[emo];
    ctx.strokeStyle  = color;
    ctx.lineWidth    = 1.5;
    ctx.globalAlpha  = 0.9;
    ctx.beginPath();

    emotionHistory.forEach((pt, i) => {{
      const x = padL + (i / (N - 1)) * cW;
      const y = padT + cH - (pt.emotions[emo] || 0) * cH;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }});
    ctx.stroke();

    // Area fill
    const lastX = padL + cW, lastY = padT + cH, firstY = padT + cH;
    ctx.globalAlpha = 0.05;
    ctx.fillStyle   = color;
    ctx.lineTo(lastX, lastY);
    ctx.lineTo(padL, firstY);
    ctx.closePath();
    ctx.fill();
    ctx.globalAlpha = 1;
  }});

  // X-axis labels
  ctx.fillStyle  = '#2a4a6a';
  ctx.font       = "8px 'Share Tech Mono', monospace";
  ctx.textAlign  = 'center';
  [0, Math.floor(N / 2), N - 1].forEach(i => {{
    if (emotionHistory[i]) {{
      const x = padL + (i / (N - 1)) * cW;
      ctx.fillText(emotionHistory[i].time, x, H - 2);
    }}
  }});

  // Build legend once
  if (!legendBuilt) {{
    const legendEl = document.getElementById('emotionLegend');
    emotions.forEach(e => {{
      const item = document.createElement('div');
      item.className = 'legend-item';
      item.innerHTML = `<div class="legend-dot" style="background:${{EMOTION_COLORS[e]}}"></div>${{e}}`;
      legendEl.appendChild(item);
    }});
    legendBuilt = true;
  }}
}}

// ── Init ───────────────────────────────────────────────
renderChat();
startWebcam();
resizeChart();
window.addEventListener('resize', () => {{ resizeChart(); drawChart(); }});
</script>
</body>
</html>
"""

    import streamlit.components.v1 as components
    components.html(interview_html, height=780, scrolling=False)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    col_end1, col_end2, col_end3 = st.columns([3, 2, 3])
    with col_end2:
        if st.button("📄 Generate Report", type="primary", use_container_width=True, key="gen_report_btn_main"):
            session_data = api_get(f"/session/{st.session_state.session_id}")
            if session_data:
                st.session_state.messages = session_data.get("conversation", st.session_state.messages)
                st.session_state.complete = session_data.get("status") == "completed"
            st.session_state.screen = "report"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "report":
    app_header()
    steps("report")
    if not st.session_state.report_text:
        with st.spinner("Generating forensic report..."):
            data = api_post(f"/report/{st.session_state.session_id}")
        if data: st.session_state.report_text = data["report"]

    if st.session_state.report_text:
        a = st.session_state.analysis or {}
        input_type = a.get("input_type", "image")
        ab1, ab2, ab3, ab4, ab5 = st.columns([1,1,1,1,2])
        with ab1:
            st.download_button("⬇️ TXT", data=st.session_state.report_text,
                file_name=f"report_{st.session_state.session_id}.txt", mime="text/plain",
                use_container_width=True, key="dl_txt")
        with ab2:
            try:
                pr = requests.get(f"{API_BASE}/report/{st.session_state.session_id}/pdf", timeout=60)
                if pr.status_code == 200:
                    st.download_button("⬇️ PDF", data=pr.content,
                        file_name=f"report_{st.session_state.session_id}.pdf", mime="application/pdf",
                        use_container_width=True, key="dl_pdf")
            except Exception: st.warning("PDF N/A")
        with ab3:
            if st.button("＋ New", use_container_width=True, key="rep_new"): reset_session(); st.rerun()
        with ab4:
            if st.button("◈ History", use_container_width=True, key="rep_hist"): st.session_state.screen="history"; st.rerun()
        with ab5:
            st.markdown(
                f"{type_badge(input_type)} &nbsp;"
                f"<b style='color:#c8d6e5;font-family:Rajdhani;'>{st.session_state.crime_type}</b>"
                f" &nbsp;<span style='color:#2a4a6a;font-family:Share Tech Mono;font-size:11px;'>"
                f"ID: {st.session_state.session_id}</span>",
                unsafe_allow_html=True)

        cr, cs = st.columns([2,1], gap="medium")
        with cr:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            sh("EVIDENCE INPUT")
            if input_type == "image":
                ec1, ec2 = st.columns([1,1])
                with ec1:
                    if st.session_state.raw_image_bytes:
                        st.image(st.session_state.raw_image_bytes, use_column_width=True)
                with ec2:
                    render_analysis_summary(a)
            elif input_type == "video":
                with st.expander(f"🎞 View {a.get('frames_analyzed',0)} analyzed frames", expanded=True):
                    render_video_frames(a.get("frame_results",[]), compact=False)
            else:
                tc1, tc2 = st.columns([1,1])
                with tc1:
                    txt = st.session_state.raw_text_input or a.get("original_text_input","")
                    st.markdown(f"<div class='text-box'>{txt}</div>", unsafe_allow_html=True)
                with tc2:
                    nlp = a.get("nlp",{})
                    if nlp.get("entities"):
                        st.markdown(mono_label("🔤 NLP ENTITIES"), unsafe_allow_html=True)
                        render_nlp_entities(nlp["entities"])
                    render_analysis_summary(a)
            st.markdown("<hr>", unsafe_allow_html=True)
            sh("INVESTIGATION REPORT")
            st.markdown(st.session_state.report_text)
            st.markdown("</div>", unsafe_allow_html=True)

        with cs:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            sh("SESSION STATS")
            q = sum(1 for m in st.session_state.messages if m["role"] == "assistant")
            w = sum(1 for m in st.session_state.messages if m["role"] == "user")
            st.metric("Input Type", input_type.capitalize())
            st.metric("Crime Type", st.session_state.crime_type or "—")
            st.metric("Questions", q)
            st.metric("Witness Answers", w)
            if input_type == "video": st.metric("Frames Analyzed", a.get("frames_analyzed",0))
            st.markdown("<hr>", unsafe_allow_html=True)
            sh("ANALYSIS SUMMARY")
            render_analysis_summary(a)
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "history":
    app_header()
    steps("upload")
    hh1, hh2 = st.columns([4,1])
    with hh1: sh("SESSION HISTORY")
    with hh2:
        if st.button("⬅ Back", key="hist_back"): st.session_state.screen="upload"; st.rerun()
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    data = api_get("/sessions")
    if data and data.get("sessions"):
        for s in data["sessions"]:
            with st.expander(
                f"◈ {s['id']} · {s['crime_type']} · "
                f"{s['created_at'][:16].replace('T',' ')} · "
                f"{'✅ Completed' if s['status']=='completed' else '🔄 Active'}",
                expanded=False
            ):
                c1, c2 = st.columns([3,1])
                if c1.button("Load Session", key="load_"+s["id"]):
                    full = api_get(f"/session/{s['id']}")
                    if full:
                        st.session_state.update({
                            "session_id": full["id"],
                            "analysis":   full["scene_analysis"],
                            "crime_type": full["crime_type"],
                            "messages":   full["conversation"],
                            "complete":   full["status"] == "completed",
                            "report_text": None,
                            "screen": "report" if full["status"] == "completed" else "interview"
                        })
                        st.rerun()
                if c2.button("🗑 Delete", key="del_"+s["id"]):
                    try:
                        requests.delete(f"{API_BASE}/session/{s['id']}", timeout=10)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    else:
        st.info("No sessions found.")
    st.markdown("</div>", unsafe_allow_html=True)