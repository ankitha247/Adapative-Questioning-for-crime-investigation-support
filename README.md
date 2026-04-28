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

crime_witness_assistant/
├── backend/
│   ├── main.py
│   ├── claude_service.py
│   ├── database.py
│   └── report_pdf.py
├── frontend/
│   └── app.py
├── .gitignore
└── requirements.txt

## Setup

1. Clone repo  
2. Create virtual environment  
3. Install requirements  
4. Add GROQ_API_KEY in .env  
5. Run backend → uvicorn main:app --reload  
6. Run frontend → streamlit run app.py  

## Features

- Image, Video, Text input
- Adaptive questioning using LLM
- NLP-based entity extraction
- Automated report generation