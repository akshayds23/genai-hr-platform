# GenAI HR Platform

An HR management platform with AI built in: employees ask an HR chatbot that answers from the company's own policies, HR screens resumes and writes job descriptions with Gemini, and everyone gets leave management, team tools and career planning in one place.

Built as the Software Engineering project (Team 24) of the IIT Madras Diploma in Data Science.

## My role

I was the backend developer and project manager. I built **the entire backend** (Flask APIs, authentication and roles, database models, the Gemini RAG chatbot, resume screening, JD generation, career planning, PDF generation and scheduled jobs) and **a large part of the Vue frontend**. I also planned the sprints and kept the team's work on track.

## What it does

**Employees**
- Ask the HR chatbot policy questions; escalate to HR when the answer is not in the knowledge base
- Apply for leave and track balances (annual, sick, casual)
- Generate a personal career path with skill gaps, and download it as a PDF
- See teammates, birthdays and project updates; send anonymous feedback

**Managers**
- Approve or reject leave with remarks, and see a team leave calendar
- Team directory, project announcements and pending offboarding tasks

**HR**
- Resume scanner: single or bulk upload, AI summaries, search and a candidate pipeline (new, shortlisted, interviewed, hired or rejected)
- Generate job descriptions with Gemini, save them and export them to PDF
- Match resumes against a job description, with a score and the reasoning behind it
- Manage the chatbot's knowledge base: FAQs, or Q&A extracted from uploaded PDF and text files
- Answer escalated questions (answers can be added back to the knowledge base)
- Analytics on headcount, leave and the applicant pipeline; letter templates; offboarding automation

## How the AI parts work

**HR chatbot (retrieval-augmented generation):**
1. HR FAQs from the database and uploaded documents are embedded with `gemini-embedding-001` (768 dimensions).
2. Incoming questions are embedded with the same model and matched using cosine similarity over cached vectors; top candidate snippets serve as grounded context.
3. Gemini (`gemini-3.1-flash-lite`) generates the final answer from that context. Unanswered questions can be escalated directly to HR.
4. When knowledge base entries change, cached embeddings refresh automatically.

**Provider fallback and limits:**
- If Gemini is unreachable or returns quota errors, the backend fails over to Groq (`openai/gpt-oss-20b`).
- In demo mode, accounts are protected by daily call limits (`AI_DAILY_LIMIT=20`, `AI_GLOBAL_DAILY_LIMIT=300`), returning HTTP 429 when exhausted.

**Resume screening and JD matching:** Resumes are parsed from PDF, DOCX or TXT files, summarized by Gemini and scored against job descriptions with structured reasoning.

**Career path planner:** Generates personalized progression milestones and downloadable PDF development plans via ReportLab.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.1, SQLAlchemy 3.1, Flask-Security-Too, Gunicorn |
| AI | Google GenAI SDK (`gemini-3.1-flash-lite`, `gemini-embedding-001`), Groq fallback |
| Documents | pypdf, python-docx, ReportLab |
| Frontend | Vue 3, Vue Router, Tailwind CSS, Axios, Vite / Vue CLI |
| Database | SQLite (local development), PostgreSQL via Neon (production) |
| Hosting & CI | Render (backend web service), Vercel (frontend static + proxy), GitHub Actions |
| Tooling | uv package manager, pytest, ruff |

## Project structure

```text
genai-hr-platform/
├── backend/
│   ├── app/
│   │   ├── api/            # Route blueprints (auth, leave, hr, teams, genai)
│   │   ├── config/         # App configuration and environment loading
│   │   ├── models/         # SQLAlchemy models (User, Role, Leave, FAQ, etc.)
│   │   ├── services/       # Core business logic (chatbot, resumes, AI client)
│   │   └── seed.py         # Demo dataset population and daily reset logic
│   ├── tests/              # In-process pytest test suite (250 tests)
│   ├── main.py             # Application entrypoint
│   └── render.yaml         # Render blueprint configuration
├── frontend/
│   ├── src/
│   │   ├── components/     # UI widgets and navigation
│   │   ├── views/          # Views for Employee, Manager, HR dashboards and Login
│   │   ├── router.js       # Client router with role-based auth guards
│   │   └── assets/         # App graphics, icons and landing screenshots
│   └── vercel.json         # Vercel routing rules and backend proxy
└── .github/workflows/ci.yml # Automated backend and frontend test CI
```

## Run it locally

### Requirements
- Python 3.12+ with [uv](https://github.com/astral-sh/uv)
- Node.js 20+
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com)

### 1. Backend setup
```bash
cd backend
cp .env.example .env
# Fill in GEMINI_API_KEY in backend/.env.
# Optional: set DEMO_MODE=true to seed demo data on first start.
uv sync
uv run python main.py
```
Backend runs at `http://127.0.0.1:5000`.

### 2. Frontend setup
```bash
cd frontend
npm install
npm run serve
```
Frontend runs at `http://localhost:8080` (requests to `/api` proxy to backend).

### Demo accounts
When demo data is seeded, use these credentials (or click the quick buttons on the login screen):
- **HR:** `hr@example.com` / `hr123`
- **Manager:** `manager@example.com` / `manager123`
- **Employee:** `employee@example.com` / `employee123`

## Tests

Run the backend test suite:
```bash
cd backend
uv run pytest -q
```

Run frontend linting:
```bash
cd frontend
npm run lint
```

## Deployment

### 1. Database (Neon)
1. Create a free PostgreSQL project on Neon.
2. Copy the connection string. Ensure the protocol is `postgresql://` or `postgresql+psycopg://`.

### 2. Backend (Render)
1. Create a new Web Service on Render linked to this repository.
2. Set Root Directory to `backend`.
3. Set Build Command to `pip install uv && uv sync --frozen --no-dev`.
4. Set Start Command to `uv run gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120` (one worker keeps the daily scheduler from running twice; the free plan has 512 MB).
5. Set Health Check Path to `/api/health`.
6. Add environment variables in Render:
   - `DATABASE_URL`: Neon PostgreSQL connection string
   - `SECRET_KEY`: Random 32+ character string
   - `SECURITY_PASSWORD_SALT`: Random 32+ character string
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GEMINI_MODEL`: `gemini-3.1-flash-lite`
   - `GEMINI_EMBED_MODEL`: `gemini-embedding-001`
   - `DEMO_MODE`: `true`
   - `AI_DAILY_LIMIT`: `20`
   - `AI_GLOBAL_DAILY_LIMIT`: `300`
   - `CRON_SECRET`: Random secret string for `/api/cron/daily`

### 3. Frontend (Vercel)
1. Import the repository into Vercel.
2. Set Root Directory to `frontend`.
3. In `frontend/vercel.json`, replace `<render-service>` with your actual Render service subdomain (e.g. `https://my-backend.onrender.com/api/$1`).
4. Set environment variable: `VUE_APP_DEMO_MODE=true`.
5. Deploy.

## Team

| Name | Role |
|---|---|
| Rishu Raj Gautam | Product Manager / Architect |
| Akshay Kumar Upadhyay | Backend Developer / PM |
| Aqdas Khan | Backend Developer / Scrum Master |
| Pinki | Frontend Developer / Tester |
| Chinavalkar Prajakta Nitin | Frontend Developer |
| Vinay Kasaudhan | Tester / Backend Developer |
| Mohd Shad | Tester / Frontend Developer |
| Sudiksha Singh | Scrum Master |

## License

MIT
