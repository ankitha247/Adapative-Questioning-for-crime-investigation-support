# Setup Guide

## 1. Install dependencies
```bash
pip install -r requirements.txt
```

## 2. Download spaCy model (required)
```bash
python -m spacy download en_core_web_sm
```

## 3. YOLO model (auto-downloads on first run)
YOLOv8n (~6MB) downloads automatically when the backend starts for the first time.
Requires internet on first launch. Subsequent runs use the cached model.

## 4. Add your Groq API key
Edit `.env` in the backend folder:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```
Get a free key at: https://console.groq.com

## 5. Run the backend
```bash
cd backend
uvicorn main:app --reload
```

## 6. Run the frontend
```bash
cd frontend
streamlit run app.py
```

## AI Pipeline Summary

| Input  | YOLO | spaCy | Groq |
|--------|------|-------|------|
| Image  | ✅ Detects objects, draws bounding boxes | — | Vision model + YOLO context |
| Video  | ✅ Per frame detection + aggregate | ✅ NLP on each frame description | Vision per frame + synthesis |
| Text   | —   | ✅ Entities, verbs, negations | Chat model + NLP context |
| Interview answers | — | ✅ Enriches each question | Better follow-up questions |
| Report | YOLO section | NLP section | Full structured report |
