"""
app.py  —  Crime Witness Interview Assistant  (v6)
Compact no-scroll UI: fixed-height panels with internal scroll where needed.
"""

import streamlit as st
import requests
import base64

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Crime Witness Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",   # collapsed by default → more content space
)

# ── Global CSS: compact, no-scroll, professional ─────────────────────────────
st.markdown("""
<style>
/* ── Global resets ─────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    height: 100vh; overflow: hidden;
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 0.6rem !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}
/* Hide default Streamlit footer/header chrome */
#MainMenu, footer, header { display: none !important; }

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
    min-width: 200px !important;
    max-width: 200px !important;
}
section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
section[data-testid="stSidebar"] button {
    font-size: 12px !important; padding: 4px 8px !important;
}

/* ── Typography ─────────────────────────────────────────── */
h1 { font-size: 1.3rem !important; margin: 0 0 4px 0 !important; }
h2 { font-size: 1.05rem !important; margin: 4px 0 !important; }
h3 { font-size: 0.95rem !important; margin: 4px 0 !important; }
p, li, div { font-size: 13px; }

/* ── Step indicator bar ─────────────────────────────────── */
.steps { display:flex; gap:12px; padding:4px 0 6px 0; }
.step-done   { color:#16a34a; font-size:12px; font-weight:600; }
.step-active { color:#2563eb; font-size:12px; font-weight:700; }
.step-todo   { color:#9ca3af; font-size:12px; }

/* ── Scrollable panels ──────────────────────────────────── */
.panel {
    height: calc(100vh - 120px);
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 6px;
}
.panel-short {
    height: calc(100vh - 160px);
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 6px;
}
.chat-panel {
    height: calc(100vh - 260px);
    overflow-y: auto;
    padding: 4px 6px;
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 8px;
}

/* ── Cards & bubbles ────────────────────────────────────── */
.scene-card {
    background:#f8f9fa; border-left:4px solid #1a1a2e;
    border-radius:6px; padding:8px 12px; margin-bottom:8px; font-size:13px;
}
.user-bubble {
    background:#e8f4fd; border-radius:12px 12px 0 12px;
    padding:7px 12px; margin:4px 0 4px 24px; font-size:13px; color:#1a1a2e;
}
.assistant-bubble {
    background:#f0f0f0; border-radius:12px 12px 12px 0;
    padding:7px 12px; margin:4px 24px 4px 0; font-size:13px; color:#1a1a2e;
}
.user-label      { color:#2563eb; font-size:11px; font-weight:600; }
.assistant-label { color:#6b7280; font-size:11px; font-weight:600; }

/* ── Badges ─────────────────────────────────────────────── */
.badge {
    display:inline-block; background:#1a1a2e; color:white;
    padding:1px 8px; border-radius:10px; font-size:11px; margin:1px 2px;
}
.badge-image { background:#2563eb; color:white; padding:2px 10px;
               border-radius:10px; font-size:12px; font-weight:600; }
.badge-video { background:#7c3aed; color:white; padding:2px 10px;
               border-radius:10px; font-size:12px; font-weight:600; }
.badge-text  { background:#059669; color:white; padding:2px 10px;
               border-radius:10px; font-size:12px; font-weight:600; }

/* ── Frame card ─────────────────────────────────────────── */
.frame-card {
    background:#faf5ff; border:1px solid #ddd6fe; border-radius:8px;
    padding:10px; margin-bottom:10px;
}
.frame-title { font-weight:700; color:#5b21b6; font-size:12px; margin-bottom:4px; }
.frame-desc {
    background:#fff; border-left:3px solid #7c3aed; border-radius:4px;
    padding:7px 10px; font-size:12px; color:#374151; line-height:1.5;
}

/* ── Text / evidence boxes ──────────────────────────────── */
.text-box {
    background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px;
    padding:10px 14px; font-size:12px; white-space:pre-wrap; color:#14532d;
    max-height:200px; overflow-y:auto;
}
.evidence-block {
    background:#fff7ed; border:1px solid #fed7aa; border-radius:8px;
    padding:10px 14px; margin-bottom:10px;
}
.evidence-title { font-weight:700; color:#92400e; font-size:13px; margin-bottom:6px; }
.input-mode-info {
    background:#f0f4ff; border-radius:6px; padding:8px 12px;
    margin-bottom:8px; font-size:12px; color:#374151;
}

/* ── Compact streamlit widgets ──────────────────────────── */
[data-testid="stTextArea"] textarea { font-size:12px !important; }
[data-testid="stSelectbox"]         { margin-bottom:4px !important; }
div[data-testid="metric-container"] { padding:4px 8px !important; }
.stButton button { font-size:12px !important; padding:4px 12px !important; }
.stDownloadButton button { font-size:12px !important; }
.stExpander { margin-bottom:4px !important; }

/* ── Upload screen how-it-works card ────────────────────── */
.how-card {
    background:#f8faff; border:1px solid #c7d2fe; border-radius:8px;
    padding:12px 16px; font-size:12px; line-height:1.7; height:100%;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

DEFAULTS = {
    "screen":          "upload",
    "session_id":      None,
    "analysis":        None,
    "messages":        [],
    "complete":        False,
    "report_text":     None,
    "crime_type":      None,
    "input_mode":      "Image",
    "raw_image_bytes": None,
    "raw_image_name":  None,
    "raw_video_bytes": None,
    "raw_video_name":  None,
    "raw_text_input":  None,
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
    labels = ["1·Upload", "2·Analysis", "3·Interview", "4·Report"]
    parts  = []
    for key, label in zip(order, labels):
        if key == current:
            parts.append(f"<span class='step-active'>▶ {label}</span>")
        elif order.index(key) < order.index(current):
            parts.append(f"<span class='step-done'>✓ {label}</span>")
        else:
            parts.append(f"<span class='step-todo'>○ {label}</span>")
    st.markdown("<div class='steps'>" + " &nbsp;›&nbsp; ".join(parts) + "</div>",
                unsafe_allow_html=True)

def type_badge(it):
    labels = {"image": "🖼️ Image", "video": "🎥 Video", "text": "📝 Text"}
    cls    = {"image": "badge-image", "video": "badge-video", "text": "badge-text"}
    return (f"<span class='{cls.get(it,'badge-image')}'>"
            f"{labels.get(it, it.capitalize())}</span>")

def render_yolo_badges(counts):
    if not counts:
        return
    badges = "".join(
        "<span style='background:#7c3aed;color:white;padding:1px 7px;"
        "border-radius:9px;font-size:11px;margin:1px 2px;display:inline-block;'>"
        + str(cnt) + "× " + lbl + "</span>"
        for lbl, cnt in sorted(counts.items(), key=lambda x: -x[1])
    )
    st.markdown(badges, unsafe_allow_html=True)

def render_nlp_entities(entities):
    if not entities:
        return
    clr = {"PERSON":"#dc2626","GPE":"#2563eb","LOC":"#0891b2","FAC":"#7c3aed",
           "ORG":"#d97706","TIME":"#059669","DATE":"#059669","EVENT":"#db2777"}
    parts = []
    for e in entities:
        c = clr.get(e["label"], "#374151")
        parts.append(
            "<span style='background:" + c + ";color:white;padding:1px 7px;"
            "border-radius:9px;font-size:11px;margin:1px 2px;display:inline-block;'"
            " title='" + e["description"] + "'>"
            + e["label"] + ": " + e["text"] + "</span>"
        )
    st.markdown("".join(parts), unsafe_allow_html=True)

def render_analysis_summary(a):
    if a.get("scene_summary"):
        st.markdown(f"<div class='scene-card'>{a['scene_summary']}</div>",
                    unsafe_allow_html=True)
    if a.get("key_objects"):
        st.markdown("**🔑 Objects**")
        st.markdown("".join(f"<span class='badge'>{o}</span>" for o in a["key_objects"]),
                    unsafe_allow_html=True)
    if a.get("observations"):
        with st.expander("👁 Observations", expanded=False):
            for obs in a["observations"]:
                st.markdown(f"• {obs}")
    if a.get("crime_indicators"):
        with st.expander("🔺 Crime Indicators", expanded=False):
            for ci in a["crime_indicators"]:
                st.markdown(f"🔺 {ci}")

def render_video_frames(frame_results, compact=False):
    if not frame_results:
        st.info("No frame data.")
        return
    for fr in frame_results:
        fn   = fr.get("frame_num", "?")
        ts   = fr.get("timestamp_sec", 0)
        jb   = fr.get("jpeg_b64", "")
        ab   = fr.get("annotated_b64", "")
        desc = fr.get("description", "")
        yc   = fr.get("yolo_counts", {})
        ne   = fr.get("nlp_entities", [])

        st.markdown(f"<div class='frame-title'>🎞 Frame {fn} · ⏱ {ts}s</div>",
                    unsafe_allow_html=True)
        if compact:
            db = ab if ab else jb
            if db:
                st.image(base64.b64decode(db), use_column_width=True)
            if yc:
                render_yolo_badges(yc)
            st.markdown(f"<div class='frame-desc'>{desc}</div>", unsafe_allow_html=True)
        else:
            ci, cd = st.columns([1, 1], gap="small")
            with ci:
                if jb and ab:
                    t1, t2 = st.tabs(["📷 Orig", "🎯 YOLO"])
                    with t1: st.image(base64.b64decode(jb), use_column_width=True)
                    with t2: st.image(base64.b64decode(ab), use_column_width=True)
                elif jb:
                    st.image(base64.b64decode(jb), use_column_width=True)
            with cd:
                if yc:
                    st.markdown("**🎯 YOLO**")
                    render_yolo_badges(yc)
                if ne:
                    st.markdown("**🔤 NLP**")
                    render_nlp_entities(ne)
                st.markdown(f"<div class='frame-desc'>{desc}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:6px 0;border-color:#e5e7eb;'>", unsafe_allow_html=True)


# ── Sidebar (always visible) ─────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔍 CWA")
    if st.button("➕ New", key="sb_new", use_container_width=True):
        reset_session(); st.rerun()
    if st.button("📋 History", key="sb_hist", use_container_width=True):
        st.session_state.screen = "history"; st.rerun()
    st.markdown("---")
    if st.session_state.session_id:
        st.caption(f"ID: `{st.session_state.session_id}`")
        if st.session_state.crime_type:
            st.caption(st.session_state.crime_type)
        if st.session_state.analysis:
            it = st.session_state.analysis.get("input_type","image")
            st.caption(MODE_ICONS.get(it.capitalize(),"📁") + " " + it.capitalize())
        st.caption(f"{len(st.session_state.messages)} messages")
    st.markdown("---")
    st.caption("Dept of CSE · Phase 1")


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.screen == "upload":
    steps("upload")
    st.markdown("### 🔍 Crime Witness Interview Assistant")

    col1, col2, col3 = st.columns([1.2, 1.2, 1], gap="medium")

    with col1:
        st.markdown("**Crime Type**")
        crime_type = st.selectbox("", CRIME_TYPES, key="crime_type_select",
                                  label_visibility="collapsed")
        st.markdown("**Input Type**")
        input_mode = st.radio("", ["Image", "Video", "Text"],
                              horizontal=True,
                              label_visibility="collapsed",
                              format_func=lambda x: MODE_ICONS[x] + " " + x,
                              key="input_mode_radio")
        st.session_state.input_mode = input_mode
        st.markdown("---")

        if input_mode == "Image":
            st.markdown("<div class='input-mode-info'>📸 Photo, CCTV still, or sketch</div>",
                        unsafe_allow_html=True)
            st.file_uploader("", type=["jpg","jpeg","png","bmp","webp","tiff","gif"],
                             key="image_uploader", label_visibility="collapsed")
            up = st.session_state.get("image_uploader")
            if up:
                st.image(up, use_column_width=True)

        elif input_mode == "Video":
            st.markdown("<div class='input-mode-info'>🎬 CCTV clip — 6 frames extracted</div>",
                        unsafe_allow_html=True)
            st.file_uploader("", type=["mp4","mov","avi","mkv","webm","flv","wmv"],
                             key="video_uploader", label_visibility="collapsed")
            uv = st.session_state.get("video_uploader")
            if uv:
                st.video(uv)
                st.caption(f"{len(uv.getvalue())/1024/1024:.1f} MB")

        else:
            st.markdown("<div class='input-mode-info'>📝 Describe the scene in writing</div>",
                        unsafe_allow_html=True)
            st.text_area("", placeholder="Describe the crime scene in detail...",
                         height=160, key="text_description_input",
                         label_visibility="collapsed")

    with col2:
        st.markdown("**How it works**")
        icon = MODE_ICONS[input_mode]
        how  = {
            "Image": "**Upload** → AI analyzes with **YOLO** detection + **Groq Vision**\n\n"
                     "**Analysis** → View original + YOLO-annotated image with detected objects\n\n"
                     "**Interview** → Adaptive questions based on visual findings\n\n"
                     "**Report** → PDF with embedded image + YOLO table",
            "Video": "**Upload** → 6 frames extracted by OpenCV\n\n"
                     "**Analysis** → Each frame: YOLO detection + Groq Vision + spaCy NLP\n\n"
                     "**Interview** → Questions based on all frames\n\n"
                     "**Report** → PDF with annotated frame grid",
            "Text":  "**Describe** → spaCy NLP extracts entities, verbs, negations\n\n"
                     "**Analysis** → Groq uses NLP findings to enrich the analysis\n\n"
                     "**Interview** → NLP enriches every follow-up question\n\n"
                     "**Report** → PDF with original text + NLP entity table",
        }
        st.markdown(f"<div class='how-card'>{how[input_mode]}</div>",
                    unsafe_allow_html=True)

    with col3:
        st.markdown("**Start**")
        if input_mode == "Image":
            up = st.session_state.get("image_uploader")
            if up:
                if st.button("🚀 Analyze Image", type="primary",
                             use_container_width=True, key="analyze_image_btn"):
                    with st.spinner("Analyzing image..."):
                        data = api_post("/analyze",
                                        files={"file":(up.name,up.getvalue(),up.type)},
                                        data={"crime_type": crime_type})
                    if data:
                        st.session_state.update({
                            "session_id":      data["session_id"],
                            "analysis":        data["analysis"],
                            "crime_type":      crime_type,
                            "raw_image_bytes": up.getvalue(),
                            "raw_image_name":  up.name,
                            "messages":        [{"role":"assistant","content":data["first_question"]}],
                            "screen":          "analysis",
                        })
                        st.rerun()
            else:
                st.info("Upload an image →")

        elif input_mode == "Video":
            uv = st.session_state.get("video_uploader")
            if uv:
                if st.button("🚀 Analyze Video", type="primary",
                             use_container_width=True, key="analyze_video_btn"):
                    with st.spinner("Extracting & analyzing frames..."):
                        data = api_post("/analyze",
                                        files={"file":(uv.name,uv.getvalue(),uv.type)},
                                        data={"crime_type": crime_type})
                    if data:
                        st.session_state.update({
                            "session_id":      data["session_id"],
                            "analysis":        data["analysis"],
                            "crime_type":      crime_type,
                            "raw_video_bytes": uv.getvalue(),
                            "raw_video_name":  uv.name,
                            "messages":        [{"role":"assistant","content":data["first_question"]}],
                            "screen":          "analysis",
                        })
                        st.rerun()
            else:
                st.info("Upload a video →")

        else:
            tv = st.session_state.get("text_description_input","").strip()
            if tv:
                if st.button("🚀 Analyze Text", type="primary",
                             use_container_width=True, key="analyze_text_btn"):
                    with st.spinner("Analyzing description..."):
                        data = api_post("/analyze/text",
                                        data={"crime_type":crime_type,"text_description":tv})
                    if data:
                        st.session_state.update({
                            "session_id":     data["session_id"],
                            "analysis":       data["analysis"],
                            "crime_type":     crime_type,
                            "raw_text_input": tv,
                            "messages":       [{"role":"assistant","content":data["first_question"]}],
                            "screen":         "analysis",
                        })
                        st.rerun()
            else:
                st.info("Enter description →")


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.screen == "analysis":
    steps("analysis")
    a          = st.session_state.analysis or {}
    input_type = a.get("input_type","image")

    # Header row
    hc1, hc2 = st.columns([4,1])
    with hc1:
        st.markdown(
            f"### 🔬 Scene Analysis &nbsp; {type_badge(input_type)} &nbsp;"
            f"<span style='font-size:13px;color:#6b7280;'>{st.session_state.crime_type}</span>",
            unsafe_allow_html=True)
    with hc2:
        if st.button("💬 Start Interview", type="primary", key="start_btn"):
            st.session_state.screen = "interview"; st.rerun()
        if st.button("🔄 Re-upload", key="reup_btn"):
            reset_session(); st.rerun()

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    if input_type == "image":
        ci, ca = st.columns([1,1], gap="medium")
        with ci:
            yolo_data = a.get("yolo",{})
            ann_b64   = yolo_data.get("annotated_b64","")
            if ann_b64 and yolo_data.get("yolo_available"):
                t1, t2 = st.tabs(["📷 Original","🎯 YOLO"])
                with t1:
                    if st.session_state.raw_image_bytes:
                        st.image(st.session_state.raw_image_bytes, use_column_width=True)
                with t2:
                    st.image(base64.b64decode(ann_b64), use_column_width=True)
            elif st.session_state.raw_image_bytes:
                st.image(st.session_state.raw_image_bytes, use_column_width=True)
            if yolo_data.get("counts"):
                st.markdown("**🎯 YOLO Detections**")
                render_yolo_badges(yolo_data["counts"])
                st.caption(yolo_data.get("summary",""))
        with ca:
            st.markdown("**🧠 AI Analysis**")
            render_analysis_summary(a)

    elif input_type == "video":
        agg = a.get("yolo_aggregate",{})
        if agg:
            st.markdown("**🎯 Aggregate YOLO (all frames)**")
            render_yolo_badges(agg)
        render_video_frames(a.get("frame_results",[]), compact=False)
        st.markdown("---")
        st.markdown("**🧠 Overall Analysis**")
        render_analysis_summary(a)

    else:
        ct, ca = st.columns([1,1], gap="medium")
        nlp = a.get("nlp",{})
        with ct:
            st.markdown("**📝 Description**")
            txt = st.session_state.raw_text_input or a.get("original_text_input","")
            st.markdown(f"<div class='text-box'>{txt}</div>", unsafe_allow_html=True)
            if nlp.get("spacy_available") and nlp.get("entities"):
                st.markdown("**🔤 spaCy Entities**")
                render_nlp_entities(nlp["entities"])
                if nlp.get("action_verbs"):
                    st.caption("Actions: " + ", ".join(nlp["action_verbs"][:6]))
                if nlp.get("negations"):
                    st.markdown(
                        "<span style='color:#dc2626;font-size:12px;'>⚠️ Negations: "
                        + ", ".join(nlp["negations"]) + "</span>",
                        unsafe_allow_html=True)
        with ca:
            st.markdown("**🧠 AI Analysis**")
            render_analysis_summary(a)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.screen == "interview":
    steps("interview")
    a          = st.session_state.analysis or {}
    input_type = a.get("input_type","image")

    col_ev, col_chat = st.columns([1, 2], gap="medium")

    with col_ev:
        st.markdown(f"**Evidence** {type_badge(input_type)}", unsafe_allow_html=True)
        st.markdown("<div class='panel-short'>", unsafe_allow_html=True)

        if input_type == "image" and st.session_state.raw_image_bytes:
            yolo = a.get("yolo",{})
            ab   = yolo.get("annotated_b64","")
            if ab:
                t1,t2 = st.tabs(["📷","🎯"])
                with t1: st.image(st.session_state.raw_image_bytes, use_column_width=True)
                with t2: st.image(base64.b64decode(ab), use_column_width=True)
            else:
                st.image(st.session_state.raw_image_bytes, use_column_width=True)
            if yolo.get("counts"):
                render_yolo_badges(yolo["counts"])

        elif input_type == "video":
            st.caption(f"🎞 {a.get('frames_analyzed',0)} frames")
            with st.expander("View frames"):
                render_video_frames(a.get("frame_results",[]), compact=True)

        elif input_type == "text":
            with st.expander("📝 Description"):
                txt = st.session_state.raw_text_input or a.get("original_text_input","")
                st.markdown(f"<div class='text-box'>{txt}</div>", unsafe_allow_html=True)

        st.markdown("---")
        render_analysis_summary(a)
        q = sum(1 for m in st.session_state.messages if m["role"]=="assistant")
        st.caption(f"Questions asked: {q}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chat:
        st.markdown("**💬 Conversation**")

        # Scrollable chat history
        chat_html = ""
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                chat_html += ("<div class='assistant-label'>🤖 Interviewer</div>"
                              f"<div class='assistant-bubble'>{msg['content']}</div>")
            else:
                chat_html += ("<div class='user-label'>👤 Witness</div>"
                              f"<div class='user-bubble'>{msg['content']}</div>")
        st.markdown(f"<div class='chat-panel'>{chat_html}</div>", unsafe_allow_html=True)

        if not st.session_state.complete:
            with st.form("answer_form", clear_on_submit=True):
                answer = st.text_area("", placeholder="Witness answer...",
                                      height=70, label_visibility="collapsed")
                cs, ce = st.columns([3,1])
                submitted = cs.form_submit_button("Send ➤", type="primary",
                                                  use_container_width=True)
                end_btn   = ce.form_submit_button("End", use_container_width=True)

            if submitted and answer.strip():
                with st.spinner("..."):
                    data = api_post(f"/respond/{st.session_state.session_id}",
                                    data={"answer": answer})
                if data:
                    st.session_state.messages.append({"role":"user","content":answer})
                    if data.get("complete"):
                        st.session_state.complete = True
                    else:
                        st.session_state.messages.append(
                            {"role":"assistant","content":data["next_question"]})
                    st.rerun()
            if end_btn:
                st.session_state.complete = True; st.rerun()

        else:
            st.success("✅ Interview complete!")
            if st.button("📄 Generate Report", type="primary",
                         use_container_width=True, key="gen_report_btn"):
                st.session_state.screen = "report"; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.screen == "report":
    steps("report")

    if not st.session_state.report_text:
        with st.spinner("Generating report..."):
            data = api_post(f"/report/{st.session_state.session_id}")
        if data:
            st.session_state.report_text = data["report"]

    if st.session_state.report_text:
        a          = st.session_state.analysis or {}
        input_type = a.get("input_type","image")

        # Action bar (top, always visible)
        ab1, ab2, ab3, ab4, ab5 = st.columns([1,1,1,1,2])
        with ab1:
            st.download_button("⬇️ TXT", data=st.session_state.report_text,
                               file_name=f"report_{st.session_state.session_id}.txt",
                               mime="text/plain", use_container_width=True, key="dl_txt")
        with ab2:
            try:
                pr = requests.get(f"{API_BASE}/report/{st.session_state.session_id}/pdf",
                                  timeout=60)
                if pr.status_code == 200:
                    st.download_button("⬇️ PDF", data=pr.content,
                                       file_name=f"report_{st.session_state.session_id}.pdf",
                                       mime="application/pdf",
                                       use_container_width=True, key="dl_pdf")
            except Exception:
                st.warning("PDF N/A")
        with ab3:
            if st.button("➕ New", use_container_width=True, key="rep_new"):
                reset_session(); st.rerun()
        with ab4:
            if st.button("📋 History", use_container_width=True, key="rep_hist"):
                st.session_state.screen = "history"; st.rerun()
        with ab5:
            st.markdown(
                f"{type_badge(input_type)} &nbsp; "
                f"<b>{st.session_state.crime_type}</b> &nbsp; "
                f"<span style='color:#6b7280;'>ID: {st.session_state.session_id}</span>",
                unsafe_allow_html=True)

        # Two-column report layout
        cr, cs = st.columns([2, 1], gap="medium")

        with cr:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)

            # Evidence input section
            st.markdown("#### 📥 Evidence Input")
            if input_type == "image":
                ec1, ec2 = st.columns([1,1])
                with ec1:
                    if st.session_state.raw_image_bytes:
                        yolo    = a.get("yolo",{})
                        ann_b64 = yolo.get("annotated_b64","")
                        if ann_b64:
                            t1,t2 = st.tabs(["📷 Original","🎯 YOLO"])
                            with t1: st.image(st.session_state.raw_image_bytes, use_column_width=True)
                            with t2: st.image(base64.b64decode(ann_b64), use_column_width=True)
                        else:
                            st.image(st.session_state.raw_image_bytes, use_column_width=True)
                with ec2:
                    yolo = a.get("yolo",{})
                    if yolo.get("counts"):
                        st.markdown("**🎯 YOLO Detections**")
                        render_yolo_badges(yolo["counts"])
                    render_analysis_summary(a)

            elif input_type == "video":
                agg = a.get("yolo_aggregate",{})
                if agg:
                    st.markdown("**Aggregate YOLO**")
                    render_yolo_badges(agg)
                with st.expander(f"🎞 View {a.get('frames_analyzed',0)} analyzed frames",
                                 expanded=True):
                    render_video_frames(a.get("frame_results",[]), compact=False)

            else:
                tc1, tc2 = st.columns([1,1])
                with tc1:
                    txt = st.session_state.raw_text_input or a.get("original_text_input","")
                    st.markdown(f"<div class='text-box'>{txt}</div>", unsafe_allow_html=True)
                with tc2:
                    nlp = a.get("nlp",{})
                    if nlp.get("entities"):
                        st.markdown("**🔤 NLP Entities**")
                        render_nlp_entities(nlp["entities"])
                    render_analysis_summary(a)

            st.markdown("---")
            st.markdown("#### 📋 Investigation Report")
            st.markdown(st.session_state.report_text)
            st.markdown("</div>", unsafe_allow_html=True)

        with cs:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("#### 📊 Session Stats")
            q = sum(1 for m in st.session_state.messages if m["role"]=="assistant")
            w = sum(1 for m in st.session_state.messages if m["role"]=="user")
            st.metric("Input Type",      input_type.capitalize())
            st.metric("Crime Type",      st.session_state.crime_type or "—")
            st.metric("Questions",       q)
            st.metric("Witness Answers", w)
            if input_type == "video":
                st.metric("Frames Analyzed", a.get("frames_analyzed",0))

            st.markdown("---")
            st.markdown("#### 🔬 Analysis Summary")
            render_analysis_summary(a)
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.screen == "history":
    steps("upload")
    hh1, hh2 = st.columns([4,1])
    with hh1: st.markdown("### 📋 Session History")
    with hh2:
        if st.button("⬅️ Back", key="hist_back"): 
            st.session_state.screen = "upload"; st.rerun()

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    data = api_get("/sessions")
    if data and data.get("sessions"):
        for s in data["sessions"]:
            with st.expander(
                f"🗂 {s['id']} · {s['crime_type']} · "
                f"{s['created_at'][:16].replace('T',' ')} · "
                f"{'✅' if s['status']=='completed' else '🔄'}",
                expanded=False
            ):
                c1, c2 = st.columns([3,1])
                if c1.button("Load", key="load_"+s["id"]):
                    full = api_get(f"/session/{s['id']}")
                    if full:
                        st.session_state.update({
                            "session_id":  full["id"],
                            "analysis":    full["scene_analysis"],
                            "crime_type":  full["crime_type"],
                            "messages":    full["conversation"],
                            "complete":    full["status"]=="completed",
                            "report_text": None,
                            "screen":      "report" if full["status"]=="completed" else "interview",
                        })
                        st.rerun()
                if c2.button("🗑", key="del_"+s["id"]):
                    try:
                        requests.delete(f"{API_BASE}/session/{s['id']}", timeout=10)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    else:
        st.info("No sessions yet.")
    st.markdown("</div>", unsafe_allow_html=True)
