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

**HR chatbot (retrieval-augmented generation)**
1. HR FAQs from the database and uploaded files are embedded with `text-embedding-004` (768 dimensions).
2. A question is embedded the same way and matched by cosine similarity (NumPy); the top 3 snippets become the context.
3. Gemini writes the answer from that context. Questions and conversations are logged, and unanswered ones can be escalated to HR.
4. When the knowledge base changes, the embeddings are rebuilt automatically.

**Resume screening and JD matching:** resumes are parsed from PDF, summarised by Gemini and scored against a job description with an explanation of the score. Bulk uploads are processed in parallel.

**Career path planner:** Gemini turns an employee's role, skills and experience into a plan with suggested next roles, skill gaps, learning resources and a 0-6, 6-18 and 18+ month timeline.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-RESTful, SQLAlchemy, Flask-Security-Too, Flask-JWT-Extended, APScheduler |
| AI | Google Gemini (`gemini-2.0-flash`), `text-embedding-004` |
| Documents | PyPDF2 for parsing, ReportLab for PDFs |
| Frontend | Vue 3, Vue Router (role-based guards), Tailwind CSS, Axios |
| Database | SQLite for development; PostgreSQL or MySQL through SQLAlchemy |
| Tooling | uv for Python packages, pytest |

## Run it locally

Requirements: Python 3.11, Node.js 18, [uv](https://github.com/astral-sh/uv) and a [Gemini API key](https://ai.google.dev).

**Backend**
```bash
cd backend
cp app/config/config.example.yaml app/config/config.yaml
# Create backend/.env with SECRET_KEY, DATABASE_URL (e.g. sqlite:///app.db) and GEMINI_API_KEY.
# Optional demo users: DEFAULT_HR_EMAIL / DEFAULT_HR_PASSWORD and the same for MANAGER and EMPLOYEE.
uv sync
uv run python main.py      # http://127.0.0.1:5000, creates and seeds the database on first run
```

**Frontend**
```bash
cd frontend
npm install
npm run serve              # http://localhost:8080, forwards /api to the backend
```

**Tests**
```bash
cd backend
uv run --with pytest --with pytest-cov pytest --cov=app
```

The chatbot's starter knowledge base is `Hr questions.pdf`, a generic HR FAQ template.

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
