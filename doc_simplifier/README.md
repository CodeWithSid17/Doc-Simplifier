# Saral — Document Simplifier (Backend, Day 1 MVP)

Django REST API that takes any confusing document and returns:
- A simplified rewrite, tuned to an audience level (child / adult / elderly / non-native)
- Extracted **warnings** (risks, penalties, deadlines that cost money)
- Extracted **actions** (concrete things the reader must do)
- Optional output in the reader's own language

Uses **Groq's free-tier API** (fast Llama 3.3 inference) — no paid services required.

## 1. Get a free Groq API key
1. Go to https://console.groq.com/keys
2. Sign up (free), create an API key
3. Copy it — you'll need it in step 3

## 2. Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure environment

```bash
cp .env.example .env
```

Open `.env` and paste your Groq key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## 4. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`

## 5. Test it

**Health check:**
```bash
curl http://127.0.0.1:8000/api/health/
```

**Simplify a document:**
```bash
curl -X POST http://127.0.0.1:8000/api/simplify/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The tenant shall vacate the premises within 30 days of notice, failing which a penalty of Rs 500 per day shall apply.",
    "audience": "elderly",
    "language": "en"
  }'
```

Expected response shape:
```json
{
  "simplified": "...",
  "warnings": ["..."],
  "actions": ["..."],
  "summary_line": "..."
}
```

`audience` options: `child`, `adult`, `elderly`, `nonnative`
`language` accepts any language name (e.g. `"Hindi"`, `"Marathi"`, `"Spanish"`) — leave as `"en"` for English.

## 6. Deploy to Render (free tier)

1. Push this project to a GitHub repo
2. Go to https://render.com → New → Web Service → connect your repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn doc_simplifier.wsgi:application`
5. Add environment variables in Render's dashboard: `GROQ_API_KEY`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=your-app.onrender.com`
6. Deploy — Render gives you a free HTTPS URL

That URL is what your Flet mobile app will call.

## Next steps (Day 2+)
- Refine prompt with real test documents (insurance, rental, medical)
- Build the Flet mobile UI (input screen + result screen)
- Add file upload (PDF/image OCR) — v2
