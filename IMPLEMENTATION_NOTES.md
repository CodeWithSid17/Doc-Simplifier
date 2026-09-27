# Saral Phase 1 implementation

This package contains the updated files for the existing `CodeWithSid17/Doc-Simplifier` project.

## What is included

- Flet 1.0.1 premium mobile UI
- DRF Token authentication retained (`Authorization: Token <token>`)
- Fixed async logout
- Authenticated document upload
- PDF/TXT/DOCX/XLSX extraction
- JPG/JPEG/PNG OCR using Tesseract
- AI simplification
- AI document summary
- Key points
- Warnings
- Action items
- Important dates
- Document-aware Ask AI
- Translation API
- Document comparison API
- PostgreSQL/Render dependency fix (`dj-database-url`)
- Docker deployment with Tesseract
- Responsive-style Flet screens

## Important

Google/Gmail OAuth and mobile OTP are not faked as working features because they require provider credentials, OAuth redirect configuration, and an actual mobile authentication callback. The current email/password authentication remains fully functional. Those providers should be added after the core deployment is verified.

## Run backend

From `doc_simplifier`:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Run mobile

From `saral_mobile`:

```powershell
python -m pip install -r requirements.txt
$env:SARAL_API_URL="http://127.0.0.1:8000"
python main.py
```

If the backend is running on another machine, replace `SARAL_API_URL` with that machine's reachable address.

## Production

Set the Render environment variables shown in `.env.example`, especially `GROQ_API_KEY` and `DATABASE_URL`.
