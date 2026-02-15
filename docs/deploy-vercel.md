# Deploy on Vercel

This project can be deployed as two Vercel services:
1. Backend (FastAPI)
2. Frontend (Vite React)

## 1) Deploy Backend to Vercel

### Create project
- In Vercel, import the same GitHub repo.
- Set **Root Directory** to: `backend`
- Framework preset: `Other`

Vercel uses `backend/vercel.json` to route requests to FastAPI.

### Backend environment variables
Set these in Vercel Project Settings -> Environment Variables:
- `COPILOT_LLM_PROVIDER` = `mock` (or `openai` / `anthropic` / `local`)
- `COPILOT_LLM_MODEL` = `gpt-4o-mini`
- `COPILOT_OPENAI_API_KEY` = `<optional>`
- `COPILOT_ANTHROPIC_API_KEY` = `<optional>`
- `COPILOT_PII_REDACTION_ENABLED` = `true`

### Verify backend
After deploy, open:
- `https://<backend-domain>/api/health`

## 2) Deploy Frontend to Vercel

### Create project
- In Vercel, import the same GitHub repo.
- Set **Root Directory** to: `frontend`
- Framework preset: `Vite`

### Frontend environment variable
Set:
- `VITE_API_BASE` = `https://<backend-domain>/api`

### Verify frontend
Open frontend URL and run the flow:
- Create Project -> Ingest -> Requirements -> Architecture -> Cloud/Cost/Risk -> Proposal

## 3) Output download location in UI
After proposal generation:
- Go to **Proposal** step.
- Check **Output Center** section.
- Click **Download** for PDF/DOCX/diagram artifacts.

Backend endpoints used by Output Center:
- `GET /api/projects/{project_id}/outputs`
- `GET /api/projects/{project_id}/outputs/{file_name}`

## Important production note
Vercel serverless file storage is ephemeral. For durable multi-user output retention, use object storage (S3/Azure Blob/GCS) and store file URLs in project records.
