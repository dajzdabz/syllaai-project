# SyllabAI Project - Claude Code Context

## Project Overview
SyllabAI is a smart syllabus management platform that transforms syllabi into synchronized calendars using AI.

**Key Features:**
- 👨‍🏫 **Professors**: Upload syllabi → AI extracts events → auto-sync to student calendars
- 🎓 **Students**: Join courses or upload their own syllabus → sync to Google Calendar

## Live Production URLs
- **Website**: https://dajzdabz.github.io/syllaai-frontend/
- **Backend API**: https://syllaai-ai.onrender.com

## Architecture
- **Frontend**: Single HTML file deployed on GitHub Pages
- **Backend**: FastAPI Python application deployed on Render
- **Database**: PostgreSQL with Alembic migrations
- **AI**: OpenAI GPT-4o-mini for syllabus parsing

## GitHub Repositories
- **Main Project**: https://github.com/dajzdabz/syllaai-project (development)
- **Frontend**: https://github.com/dajzdabz/syllaai-frontend (GitHub Pages deployment)
- **Backend**: https://github.com/dajzdabz/syllaai-backend (Render auto-deploy)

## Key API Endpoints
- `POST /api/auth/google` - Google OAuth authentication
- `GET /api/courses/` - List user's courses
- `POST /api/courses/` - Create new course (professors)
- `POST /api/courses/student-syllabus` - Process student-uploaded syllabus
- `POST /api/courses/{course_id}/syllabus` - Process professor syllabus
- `POST /api/courses/{course_id}/events/publish` - Publish events to students

## Environment Variables (Backend)
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your_secret_key
OPENAI_API_KEY=sk-proj-...
GOOGLE_CLIENT_ID=208074157418-...
GOOGLE_CLIENT_SECRET=GOCSPX-...
DEBUG=true
```

## Quick Commands

### Deploy Frontend Changes
```bash
# Frontend is in separate repo - need to push changes there
# Local frontend file: D:\SyllabAI\frontend\index.html
```

### Deploy Backend Changes
```bash
cd "D:\SyllabAI\backend"
git add .
git commit -m "Your changes"
git push  # Auto-deploys to Render
```

### Local Development
```bash
cd "D:\SyllabAI\backend"
uvicorn app.main:app --reload  # Backend on localhost:8000
```

## Current Status ✅
- **Website**: Live at https://dajzdabz.github.io/syllaai-frontend/
- **Backend**: Live at https://syllaai-ai.onrender.com
- **AI Processing**: Upgraded to GPT-4o-mini (July 12, 2025)
- **Syllabus Upload**: Working with enhanced text extraction
- **Google OAuth**: Functional
- **Database**: Migrations working

## Important Files
- `D:\SyllabAI\frontend\index.html` - Frontend app (deploy to syllaai-frontend repo)
- `D:\SyllabAI\backend\app\routers\courses.py` - Main syllabus processing
- `D:\SyllabAI\backend\app\services\openai_service.py` - GPT-4o-mini integration
- `D:\SyllabAI\backend\.env` - Environment variables (not in git)

---
*Last Updated: July 12, 2025*
*Status: Production ready with GPT-4o-mini integration*