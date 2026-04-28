"""
main.py
FastAPI backend for the AI Crime Witness Interview Assistant.
Supports: Image, Video, and Text input for scene analysis.
"""

import os
import io
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
_env_backend = BASE_DIR / ".env"
_env_root    = BASE_DIR.parent / ".env"
if _env_backend.exists():
    load_dotenv(_env_backend)
    print(f"[INFO] Loaded .env from: {_env_backend}")
elif _env_root.exists():
    load_dotenv(_env_root)
    print(f"[INFO] Loaded .env from: {_env_root}")
else:
    print("[WARN] No .env file found!")

_key = os.getenv("GROQ_API_KEY", "")
if not _key or _key == "your-groq-key-here":
    print("[ERROR] GROQ_API_KEY is not set or still has the placeholder value!")
else:
    print(f"[INFO] GROQ_API_KEY loaded (starts with: {_key[:12]}...)")

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image

from database import (
    init_db, create_session, get_session, add_message,
    complete_session, save_report, list_sessions,
)
from claude_service import analyze_image, analyze_video, analyze_text, get_next_question, generate_report
from report_pdf import generate_pdf

app = FastAPI(title="Crime Witness Assistant API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
init_db()
print("[INFO] Database initialised.")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"\n[ERROR] {request.url}\n{tb}")
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": tb})


def _normalise_image(image_bytes: bytes, filename: str) -> tuple:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        print(f"[INFO] Image normalised ({len(buf.getvalue())} bytes)")
        return buf.getvalue(), "image.jpg"
    except Exception as e:
        print(f"[WARN] Image normalisation failed: {e}")
        return image_bytes, filename


@app.get("/")
def root():
    key_ok = bool(_key) and _key != "your-groq-key-here"
    return {"status": "ok", "message": "Crime Witness Assistant API v3.0", "api_key_loaded": key_ok}


# ── Text-only analysis (no file) ──────────────────────────────────────────────

@app.post("/analyze/text")
async def analyze_text_route(crime_type: str = Form(...), text_description: str = Form(...)):
    """Analyze a text description of a crime scene."""
    print(f"\n[/analyze/text] crime_type={crime_type}")

    if not _key or _key == "your-groq-key-here":
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")

    if not text_description.strip():
        raise HTTPException(status_code=400, detail="Text description cannot be empty.")

    analysis = analyze_text(text_description.strip(), crime_type)
    sid      = create_session(crime_type, analysis, None)
    first_q  = analysis.get("first_question", "Can you describe what you witnessed?")
    add_message(sid, "assistant", first_q)
    print(f"[/analyze/text] Session created: {sid}")

    return {"session_id": sid, "analysis": analysis, "first_question": first_q}


# ── File (image or video) analysis ───────────────────────────────────────────

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), crime_type: str = Form(...)):
    """Analyze an uploaded image or video file."""
    print(f"\n[/analyze] crime_type={crime_type}  filename={file.filename}")

    if not _key or _key == "your-groq-key-here":
        raise HTTPException(status_code=500,
            detail="GROQ_API_KEY is not set. Edit your .env file and restart the server.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    print(f"[/analyze] Received {len(raw_bytes)} bytes")

    ext = Path(file.filename or "").suffix.lower()

    if ext in VIDEO_EXTS:
        # Video path
        save_path = UPLOAD_DIR / (file.filename or "video.mp4")
        save_path.write_bytes(raw_bytes)
        print("[/analyze] Calling Video Analysis...")
        analysis = analyze_video(raw_bytes, crime_type, file.filename or "video.mp4")

    elif ext in IMAGE_EXTS or ext == "":
        # Image path
        image_bytes, safe_name = _normalise_image(raw_bytes, file.filename or "image.jpg")
        save_path = UPLOAD_DIR / safe_name
        save_path.write_bytes(image_bytes)
        print("[/analyze] Calling Image Vision API...")
        analysis = analyze_image(image_bytes, crime_type, safe_name)

    else:
        raise HTTPException(status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload an image or video file.")

    print(f"[/analyze] Analysis keys: {list(analysis.keys())}")

    # Strip large base64 frame images before saving to DB; keep in API response
    import copy
    analysis_for_db = copy.deepcopy(analysis)
    if "frame_results" in analysis_for_db:
        analysis_for_db["frame_results"] = [
            {k: v for k, v in fr.items() if k not in ("jpeg_b64",)}
            for fr in analysis_for_db["frame_results"]
        ]

    sid     = create_session(crime_type, analysis_for_db, str(save_path))
    first_q = analysis.get("first_question", "Can you describe what you witnessed?")
    add_message(sid, "assistant", first_q)
    print(f"[/analyze] Session created: {sid}")

    # Return full analysis (with b64 frame images) to frontend
    return {"session_id": sid, "analysis": analysis, "first_question": first_q}


@app.post("/respond/{session_id}")
async def respond(session_id: str, answer: str = Form(...)):
    print(f"\n[/respond] session={session_id}")
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    if session["status"] == "completed":
        return {"complete": True, "next_question": "", "message": "Interview already completed."}
    if not answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    add_message(session_id, "user", answer)
    session = get_session(session_id)
    scene_ctx = (
        f"Scene summary: {session['scene_analysis'].get('scene_summary', '')}\n"
        f"Key objects: {', '.join(session['scene_analysis'].get('key_objects', []))}\n"
        f"Crime indicators: {', '.join(session['scene_analysis'].get('crime_indicators', []))}"
    )

    next_q = get_next_question(session["conversation"], scene_ctx, session["crime_type"])
    print(f"[/respond] Response: {next_q[:80]}...")

    if "[INTERVIEW_COMPLETE]" in next_q:
        complete_session(session_id)
        return {"complete": True, "next_question": "", "message": "Interview complete."}

    add_message(session_id, "assistant", next_q)
    return {"complete": False, "next_question": next_q}


@app.post("/report/{session_id}")
async def get_report(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    report_text = generate_report(
        session["scene_analysis"], session["conversation"],
        session["crime_type"], session_id,
    )
    save_report(session_id, report_text)
    return {"session_id": session_id, "report": report_text}


@app.get("/report/{session_id}/pdf")
async def download_pdf(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    report_text = generate_report(
        session["scene_analysis"], session["conversation"],
        session["crime_type"], session_id,
    )
    sa         = session["scene_analysis"]
    input_type = sa.get("input_type", "image")

    image_bytes    = None
    image_filename = None
    frame_results  = None
    frames_n       = 0
    nlp_data       = None
    original_text  = None

    if input_type == "image":
        img_path = session.get("image_path")
        if img_path and Path(img_path).exists():
            image_bytes    = Path(img_path).read_bytes()
            image_filename = Path(img_path).name
    elif input_type == "video":
        frames_n      = sa.get("frames_analyzed", 0)
        frame_results = sa.get("frame_results", [])
    elif input_type == "text":
        original_text = sa.get("original_text_input", "")
        nlp_data      = sa.get("nlp", {})

    pdf_bytes = generate_pdf(
        report_text, session_id, session["crime_type"],
        image_bytes=image_bytes, image_filename=image_filename,
        frame_results=frame_results, frames_n=frames_n,
        nlp_data=nlp_data, original_text=original_text,
        input_type=input_type,
    )
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{session_id}.pdf"'})


@app.get("/session/{session_id}")
async def get_session_data(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return session


@app.get("/sessions")
async def get_all_sessions():
    return {"sessions": list_sessions()}


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    import sqlite3
    from database import DB_PATH
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.execute("DELETE FROM reports WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"message": f"Session {session_id} deleted."}