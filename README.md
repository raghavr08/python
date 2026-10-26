# ResumeIQ

AI-powered resume-to-job comparison with an evidence-first dashboard, safe rewrite workspace, and interview practice.

## Run the frontend

The published UI is a static experience with a separately-labelled demo path. For a local build:

```powershell
node build.mjs
```

Serve `dist/` using any static server.

## Run the secure API

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item ..\.env.example .env
uvicorn main:app --reload --port 8000
```

`POST /api/resume/upload` safely validates PDF, DOCX, and TXT files and extracts real text. `POST /api/resume/analyze` calculates validated deterministic component scores. It is the intended server-side location for an OpenAI/Gemini integration: keep API keys in environment variables, validate structured model output, and compute the final weighted score in Python.

## Deployment

Deploy `dist/` to a static frontend host (Vercel/Cloudflare Pages). Deploy `backend/` to a Python-compatible host (Render/Railway/Fly.io), then set the frontend API base URL and `CORS_ORIGINS`. The included Sites deployment hosts the polished frontend privately; it does not embed any secret or AI key.
