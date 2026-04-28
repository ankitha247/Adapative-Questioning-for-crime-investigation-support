"""
claude_service.py
AI interactions using Groq API (free tier).

Pipeline per input type:
  Image  → Groq Vision analyzes image directly
  Video  → extract frames → Groq Vision on each frame + spaCy NLP
         → Groq synthesis of all frame descriptions
  Text   → spaCy NLP on description → Groq with entity context injected

Interview:
  Each witness answer → spaCy NLP → entity/phrase context
  injected into Groq interviewer system prompt for richer follow-up questions

Report:
  spaCy NLP summary included as a dedicated section
"""

import os
import base64
import json
import re
import cv2
import tempfile
from pathlib import Path
from dotenv import load_dotenv

_base = Path(__file__).resolve().parent
load_dotenv(_base / ".env")
load_dotenv(_base.parent / ".env")

from groq import Groq
from nlp_service import analyze_text as nlp_analyze, enrich_conversation_context

_api_key = os.getenv("GROQ_API_KEY", "")
if not _api_key or _api_key == "your-groq-key-here":
    print("[ERROR] GROQ_API_KEY is not set.")
else:
    print(f"[INFO] GROQ_API_KEY loaded (starts with: {_api_key[:8]}...)")

client = Groq(api_key=_api_key, timeout=120.0)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
CHAT_MODEL   = "llama-3.3-70b-versatile"


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().replace("```", "").strip()
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in:\n{text[:300]}")
    return json.loads(text[start:end])


def _extract_video_frames(video_bytes: bytes, num_frames: int = 6) -> list:
    """Extract evenly-spaced frames. Returns list of dicts with jpeg_bytes + timestamp."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    frames = []
    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps          = cap.get(cv2.CAP_PROP_FPS) or 25
        print(f"[Video] total={total_frames}, fps={fps:.1f}, duration={total_frames/fps:.1f}s")

        margin  = max(1, int(total_frames * 0.05))
        usable  = total_frames - 2 * margin
        step    = max(1, usable // num_frames)
        indices = [margin + i * step for i in range(num_frames)]

        for frame_num, idx in enumerate(indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            _, buf     = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            jpeg_bytes = buf.tobytes()
            timestamp  = round(idx / fps, 2)
            frames.append({
                "frame_num":     frame_num + 1,
                "frame_index":   idx,
                "jpeg_bytes":    jpeg_bytes,
                "timestamp_sec": timestamp,
            })
            print(f"[Video] Frame {frame_num+1} @ {timestamp}s: {len(jpeg_bytes)} bytes")

        cap.release()
    finally:
        os.unlink(tmp_path)

    return frames


def analyze_image(image_bytes: bytes, crime_type: str, filename: str = "image.jpg") -> dict:
    """Groq Vision analyzes the image directly — no YOLO pre-processing."""
    ext  = Path(filename).suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png",  ".gif":  "image/gif",
            ".webp": "image/webp"}.get(ext, "image/jpeg")

    b64      = base64.standard_b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"

    prompt = f"""You are an experienced forensic scene analyst.
A {crime_type} case is being investigated.

Carefully examine the attached image (photograph, CCTV still, sketch, or diagram).

Respond with ONLY a valid JSON object — no extra text, no markdown:

{{
  "scene_summary": "2-3 sentence factual description of what you see",
  "key_objects": ["all", "relevant", "objects", "and", "evidence", "observed"],
  "observations": ["notable", "forensic", "details", "about", "the", "scene"],
  "crime_indicators": ["elements", "that", "relate", "to", "the", "crime", "type"],
  "first_question": "The single most important opening question for the witness"
}}

If the image is unclear, describe what you can see and note the limitations.
Always analyze — never refuse."""

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text",      "text": prompt},
            ],
        }],
        max_tokens=1024,
    )
    raw = response.choices[0].message.content
    print(f"[Groq Vision/Image] {raw[:200]}")

    try:
        result = _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        result = {
            "scene_summary":  raw[:400] if raw else "Image analyzed.",
            "key_objects":    [], "observations": [], "crime_indicators": [],
            "first_question": "Can you describe what you witnessed at the scene?",
            "_parse_error":   str(e),
        }

    result["input_type"] = "image"
    return result


def analyze_video(video_bytes: bytes, crime_type: str, filename: str = "video.mp4") -> dict:
    """
    Video analysis: extract frames → Groq Vision per frame + spaCy NLP
    → Groq synthesis of all frame descriptions
    """
    print(f"[Video] Analyzing {filename}, {len(video_bytes)} bytes")

    frames = _extract_video_frames(video_bytes, num_frames=6)
    if not frames:
        return {
            "scene_summary": "Could not extract frames.",
            "key_objects": [], "observations": ["Video could not be processed."],
            "crime_indicators": [], "first_question": "Can you describe what you witnessed?",
            "input_type": "video", "frames_analyzed": 0,
            "frame_results": [], "frame_descriptions": [],
        }

    frame_results      = []
    frame_descriptions = []

    for f in frames:
        frame_num  = f["frame_num"]
        jpeg_bytes = f["jpeg_bytes"]
        timestamp  = f["timestamp_sec"]
        print(f"[Video] Frame {frame_num}/{len(frames)} @ {timestamp}s")

        b64      = base64.standard_b64encode(jpeg_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"

        prompt = f"""You are a forensic analyst reviewing frame {frame_num} of {len(frames)}
from a {crime_type} incident video (timestamp: {timestamp}s).

Describe what you observe:
- The scene, location, and environment
- All people visible (appearance, actions, position)
- All vehicles and objects of interest
- Any notable actions or events occurring

Be specific, factual, and 3-5 sentences."""

        description = f"Frame {frame_num}: Could not analyze."
        try:
            resp = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text",      "text": prompt},
                    ],
                }],
                max_tokens=400,
            )
            description = resp.choices[0].message.content.strip()
            print(f"[Video] Frame {frame_num} → {description[:80]}...")
        except Exception as e:
            print(f"[WARN] Frame {frame_num} Groq failed: {e}")

        nlp_result = nlp_analyze(description)

        frame_results.append({
            "frame_num":     frame_num,
            "timestamp_sec": timestamp,
            "jpeg_b64":      base64.standard_b64encode(jpeg_bytes).decode(),
            "description":   description,
            "nlp_entities":  nlp_result["entities"],
            "nlp_summary":   nlp_result["entity_summary"],
        })
        frame_descriptions.append(
            f"Frame {frame_num} ({timestamp}s): {description}"
        )

    synthesis_prompt = f"""You are a senior forensic analyst.
Below are descriptions of {len(frames)} evenly-spaced frames from a {crime_type} incident video.

{chr(10).join(frame_descriptions)}

Respond with ONLY a valid JSON object — no extra text, no markdown:

{{
  "scene_summary": "2-3 sentence overall summary of the full video sequence",
  "key_objects": ["all", "significant", "objects", "people", "vehicles", "observed"],
  "observations": ["key", "patterns", "and", "details", "across", "all", "frames"],
  "crime_indicators": ["elements", "that", "confirm", "the", "crime", "type"],
  "first_question": "The most important opening question for the witness based on all frames"
}}"""

    try:
        synth_resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": synthesis_prompt}],
            max_tokens=1024,
        )
        result = _extract_json(synth_resp.choices[0].message.content)
    except Exception as e:
        print(f"[WARN] Synthesis failed: {e}")
        result = {
            "scene_summary": " ".join(d.split(": ", 1)[-1] for d in frame_descriptions[:2]),
            "key_objects": [], "observations": frame_descriptions,
            "crime_indicators": [],
            "first_question": "Can you describe what you saw in the video footage?",
        }

    result["input_type"]         = "video"
    result["frames_analyzed"]    = len(frames)
    result["frame_results"]      = frame_results
    result["frame_descriptions"] = frame_descriptions
    return result


def analyze_text(text_input: str, crime_type: str) -> dict:
    """spaCy NLP → Groq with entity context injected."""
    print(f"[Text] Analyzing {len(text_input)} chars")

    nlp_result  = nlp_analyze(text_input)
    nlp_context = nlp_result["context_enrichment"]
    print(f"[Text] NLP enrichment: {nlp_context[:120]}")

    prompt = f"""You are an experienced forensic scene analyst.
A {crime_type} case is being investigated.

The witness/officer provided this written description:
\"\"\"{text_input}\"\"\"

NLP Pre-Analysis (spaCy):
{nlp_context if nlp_context else "No named entities detected."}

Using the text AND the NLP findings above, respond with ONLY a valid JSON object:

{{
  "scene_summary": "2-3 sentence factual summary integrating text and NLP findings",
  "key_objects": ["items", "people", "locations", "from", "text", "and", "NLP"],
  "observations": ["notable", "details", "including", "NLP", "entities", "found"],
  "crime_indicators": ["elements", "related", "to", "the", "crime", "type"],
  "first_question": "The most important follow-up question for the witness"
}}"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    raw = response.choices[0].message.content
    print(f"[Text/Groq] {raw[:200]}")

    try:
        result = _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        result = {
            "scene_summary": text_input[:300], "key_objects": [],
            "observations": [], "crime_indicators": [],
            "first_question": "Can you elaborate on what you witnessed?",
            "_parse_error":  str(e),
        }

    result["input_type"]          = "text"
    result["original_text_input"] = text_input
    result["nlp"] = {
        "entities":        nlp_result["entities"],
        "entity_summary":  nlp_result["entity_summary"],
        "noun_phrases":    nlp_result["noun_phrases"],
        "action_verbs":    nlp_result["action_verbs"],
        "negations":       nlp_result["negations"],
        "spacy_available": nlp_result["spacy_available"],
    }
    return result


def get_next_question(conversation: list, scene_context: str, crime_type: str) -> str:
    """Adaptive interview question with spaCy NLP enrichment."""
    nlp_enrichment = enrich_conversation_context(conversation)

    system_prompt = f"""You are a professional forensic interviewer trained in the
Cognitive Interview technique. You are interviewing a witness for a {crime_type} case.

Scene context from analysis:
{scene_context}
{nlp_enrichment}

Rules:
1. Ask exactly ONE focused open-ended question per turn.
2. Build directly on what the witness just said.
3. Use NLP-identified entities (people, places, times) as specific follow-up targets.
4. Cover progressively: people seen, timeline, physical descriptions, sounds/smells, location.
5. Use probing follow-ups for vague answers.
6. Never lead the witness or suggest answers.
7. Keep tone calm, neutral, professional.
8. After covering all major areas (roughly 8-12 exchanges), output ONLY:
   [INTERVIEW_COMPLETE]
   Do NOT output this prematurely."""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": system_prompt}, *conversation],
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


def generate_report(scene_analysis: dict, conversation: list,
                    crime_type: str, session_id: str) -> str:
    """Generate structured forensic report with NLP analysis. No YOLO section."""
    input_type = scene_analysis.get("input_type", "image")

    if input_type == "video":
        frames_n    = scene_analysis.get("frames_analyzed", 0)
        frame_descs = scene_analysis.get("frame_descriptions", [])
        input_section = (
            f"Input Type     : Video footage\n"
            f"Frames Analyzed: {frames_n}\n\n"
            f"Per-Frame Analysis:\n"
            + ("\n".join(frame_descs) if frame_descs else "Not available.")
        )
        nlp_section = "NLP analysis applied per frame — see frame descriptions above."

    elif input_type == "text":
        original_text = scene_analysis.get("original_text_input", "Not available.")
        nlp_data      = scene_analysis.get("nlp", {})
        input_section = (
            f"Input Type     : Text description\n\n"
            f"Original Description:\n\"\"\"{original_text}\"\"\""
        )
        nlp_section = nlp_data.get("entity_summary", "No NLP data available.")
        if nlp_data.get("action_verbs"):
            nlp_section += f"\nActions described: {', '.join(nlp_data['action_verbs'][:8])}"
        if nlp_data.get("negations"):
            nlp_section += f"\nNegations (witness said did NOT see): {', '.join(nlp_data['negations'])}"

    else:  # image
        input_section = "Input Type     : Image / photograph"
        nlp_section   = "NLP analysis applied to witness interview answers (see transcript)."

    all_witness_text = " ".join(m["content"] for m in conversation if m["role"] == "user")
    interview_nlp    = nlp_analyze(all_witness_text) if all_witness_text else {}
    interview_nlp_summary = (
        interview_nlp.get("entity_summary", "") if interview_nlp.get("spacy_available") else ""
    )
    negations_in_interview = interview_nlp.get("negations", []) if interview_nlp else []

    transcript = "\n\n".join([
        f"{'Interviewer' if m['role'] == 'assistant' else 'Witness'}: {m['content']}"
        for m in conversation
    ])

    prompt = f"""You are a senior forensic report writer. Generate a formal investigation report.

=== CASE METADATA ===
Case ID    : {session_id}
Crime Type : {crime_type}

=== EVIDENCE INPUT ===
{input_section}

=== NLP ANALYSIS (spaCy) ===
{nlp_section}
Interview NLP summary: {interview_nlp_summary if interview_nlp_summary else "N/A"}
Witness negations: {", ".join(negations_in_interview) if negations_in_interview else "None detected"}

=== SCENE ANALYSIS ===
Summary    : {scene_analysis.get("scene_summary", "N/A")}
Key Objects: {", ".join(scene_analysis.get("key_objects", []))}
Observations: {"; ".join(scene_analysis.get("observations", []))}
Indicators : {"; ".join(scene_analysis.get("crime_indicators", []))}

=== WITNESS INTERVIEW TRANSCRIPT ===
{transcript}

=== REQUIRED SECTIONS (use ## for each header) ===
## Case Summary
## Evidence Input
## NLP Analysis of Witness Statements
## Scene Description
## Physical Evidence Identified
## Witness Statement Summary
## Persons / Vehicles Described
## Timeline of Events
## Inconsistencies or Gaps
## Investigator Recommendations

For the NLP section: list extracted entities (persons, locations, times), key phrases,
action verbs, and any negations (what the witness said they did NOT see — important gaps).
Be factual, concise, and objective. Use professional forensic language."""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return response.choices[0].message.content