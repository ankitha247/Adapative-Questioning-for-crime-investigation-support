import sqlite3
import json
import uuid
from datetime import datetime

DB_PATH = "cases.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          TEXT PRIMARY KEY,
            crime_type  TEXT NOT NULL,
            scene_analysis TEXT NOT NULL,
            conversation   TEXT NOT NULL DEFAULT '[]',
            image_path     TEXT,
            created_at     TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'active'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id          TEXT PRIMARY KEY,
            session_id  TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def create_session(crime_type: str, scene_analysis: dict, image_path: str = None) -> str:
    """Create a new interview session and return its ID."""
    sid = str(uuid.uuid4())[:8].upper()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            sid,
            crime_type,
            json.dumps(scene_analysis),
            "[]",
            image_path,
            datetime.now().isoformat(),
            "active",
        ),
    )
    conn.commit()
    conn.close()
    return sid


def get_session(sid: str) -> dict | None:
    """Fetch a session by ID. Returns None if not found."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "crime_type": row[1],
        "scene_analysis": json.loads(row[2]),
        "conversation": json.loads(row[3]),
        "image_path": row[4],
        "created_at": row[5],
        "status": row[6],
    }


def add_message(sid: str, role: str, content: str):
    """Append a message to the conversation history of a session."""
    session = get_session(sid)
    if not session:
        raise ValueError(f"Session {sid} not found")
    conversation = session["conversation"]
    conversation.append({"role": role, "content": content})
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE sessions SET conversation = ? WHERE id = ?",
        (json.dumps(conversation), sid),
    )
    conn.commit()
    conn.close()


def complete_session(sid: str):
    """Mark a session as completed."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sessions SET status = 'completed' WHERE id = ?", (sid,))
    conn.commit()
    conn.close()


def save_report(session_id: str, content: str) -> str:
    """Save a generated report and return its ID."""
    rid = str(uuid.uuid4())[:8].upper()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO reports VALUES (?, ?, ?, ?)",
        (rid, session_id, content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return rid


def list_sessions() -> list[dict]:
    """Return all sessions ordered by newest first."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, crime_type, created_at, status FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "crime_type": r[1], "created_at": r[2], "status": r[3]}
        for r in rows
    ]