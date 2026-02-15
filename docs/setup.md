# Setup Guide

## Prerequisites
- Python 3.10+
- Node 18+
- Optional for Mermaid diagram rendering: `@mermaid-js/mermaid-cli` (`mmdc`)

## Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts_generate_samples.py
uvicorn app.main:app --reload --port 8000
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

Note:
- Frontend now defaults to `/api` and uses Vite proxy to `http://localhost:8000`.
- If you deploy frontend separately, set `VITE_API_BASE` explicitly (example: `http://your-backend-host:8000/api`).

## Optional Environment Variables
- `COPILOT_LLM_PROVIDER=mock|openai|anthropic|local`
- `COPILOT_LLM_MODEL=gpt-4o-mini`
- `COPILOT_OPENAI_API_KEY=<key>`
- `COPILOT_ANTHROPIC_API_KEY=<key>`
- `COPILOT_LOCAL_LLM_BASE_URL=http://localhost:11434`
- `COPILOT_VECTOR_PROVIDER=faiss_local`
- `COPILOT_PII_REDACTION_ENABLED=true`
- `COPILOT_ENCRYPTION_KEY=<fernet_key_base64>`

## Mermaid Export (Step 3)
If `mmdc` is installed, architecture Mermaid is exported to real `.svg` and `.png`.
If `mmdc` is missing, backend falls back to placeholder SVG and empty PNG files.

Install Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli
```
