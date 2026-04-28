# AI Crime Witness Interview Assistant

AI-powered eyewitness interview system supporting **Image**, **Video**, and **Text** input
for scene analysis and adaptive questioning.

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| AI        | Groq API (Vision + Chat, free tier) |
| Backend   | FastAPI + Python 3.11+              |
| Frontend  | Streamlit                           |
| Database  | SQLite (zero config)                |
| PDF       | ReportLab                           |
| Video     | OpenCV (frame extraction)           |

## Project Structure

```
crime_witness_assistant/
├── backend/
│   ├── main.py            ← FastAPI routes (image, video, text)
│   ├── claude_service.py  ← All AI calls (analyze_image, analyze_video, analyze_text)
│   ├── database.py        ← SQLite operations
│   └── report_pdf.py      ← PDF generation
├── frontend/
│   └── app.py             ← Streamlit UI (3 input modes)
├── .env                   ← API key (never commit this)
├── .gitignore
└── requirements.txt
```

## Input Modes

| Mode  | Description                                              |
|-------|----------------------------------------------------------|
| 🖼️ Image | Upload a photo, CCTV still, sketch, or diagram       |
| 🎥 Video | Upload a CCTV clip — 6 frames auto-extracted & analyzed |
| 📝 Text  | Paste a written description when no media is available |

## Setup

### 1. Clone / open in VS Code

```bash
git clone <your-repo-url>
cd crime_witness_assistant
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `opencv-python-headless` is required for video frame extraction.

### 4. Add your Groq API key

Edit `.env`:
```
GROQ_API_KEY=your-groq-key-here
```

Get a free key at: https://console.groq.com

### 5. Run the backend

```bash
cd backend
uvicorn main:app --reload
```
Backend runs at http://localhost:8000

### 6. Run the frontend

```bash
cd frontend
streamlit run app.py
```
Frontend runs at http://localhost:8501

## Usage

1. Choose a crime type from the dropdown
2. Select input mode: **Image**, **Video**, or **Text**
3. Upload your file or enter a description
4. Read the AI's scene analysis
5. Answer the adaptive questions as the witness
6. Download the generated PDF/TXT investigation report

## Report Sections

The generated report includes an **Evidence Input** section that varies by input type:
- **Image**: Notes the image was used as visual evidence
- **Video**: Lists number of frames analyzed + per-frame descriptions
- **Text**: Reproduces the original written description

## API Endpoints

| Method | Endpoint                   | Description                         |
|--------|----------------------------|-------------------------------------|
| POST   | /analyze                   | Upload image or video, get analysis |
| POST   | /analyze/text              | Submit text description             |
| POST   | /respond/{session_id}      | Send answer, get next question      |
| POST   | /report/{session_id}       | Generate text report                |
| GET    | /report/{session_id}/pdf   | Download PDF report                 |
| GET    | /session/{session_id}      | Get session data                    |
| GET    | /sessions                  | List all sessions                   |
| DELETE | /session/{session_id}      | Delete a session                    |

## Accepted File Formats

**Images:** JPG, JPEG, PNG, BMP, WEBP, TIFF, GIF  
**Videos:** MP4, MOV, AVI, MKV, WEBM, FLV, WMV

## Team

- Shreeraksha - 1MJ23CS176
- Sinchana    - 1MJ23CS183
- Soujanya   - 1MJ23CS185
- Sukanya     - 1MJ23CS188

Guide: Prof. KL Sujitha · Dept of CSE
