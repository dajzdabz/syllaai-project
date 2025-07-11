# app/main.py – FIXED CORS FOR PRODUCTION
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, courses, events
from app.database import engine, Base
import os

# ------------------------------------------------------------------ #
#  Error-handling middleware (unchanged)
# ------------------------------------------------------------------ #
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except IntegrityError as exc:
            logger.error(f"Database integrity error: {exc}")
            return JSONResponse(
                {"detail": "Database constraint violation", "error": str(exc)},
                status_code=400,
            )
        except ValidationError as exc:
            logger.error(f"Validation error: {exc}")
            return JSONResponse(
                {"detail": "Validation failed", "errors": exc.errors()},
                status_code=422,
            )
        except Exception as exc:
            logger.error(f"Unexpected error: {exc}")
            return JSONResponse(
                {"detail": "Internal server error", "error": str(exc)},
                status_code=500,
            )

# ------------------------------------------------------------------ #
#  Database setup
# ------------------------------------------------------------------ #
Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------ #
#  FastAPI app
# ------------------------------------------------------------------ #
app = FastAPI(
    title="SyllabAI Backend",
    description="API for managing academic courses and events",
    version="1.0.0",
)

# Add error middleware first
app.add_middleware(ErrorMiddleware)

# ------------------------------------------------------------------ #
#  CORS CONFIGURATION (NOW ALLOWS GITHUB PAGES + CUSTOM DOMAINS)
# ------------------------------------------------------------------ #
ENV = os.getenv("ENVIRONMENT", "development").lower()

if ENV == "production":
    # Domains that should be able to call this API in prod
    allow_origins = [
        "https://dajzdabz.github.io",
        "https://syllaai.com",
        "https://app.syllaai.com",
    ]
else:
    # Local/dev front-end origins
    allow_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    # Allow any GitHub Pages subdomain just in case (e.g. username.github.io)
    allow_origin_regex=r"https://.*\.github\.io",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
#  Health-check endpoints
# ------------------------------------------------------------------ #
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "syllaai-backend"}

@app.get("/healthz")
async def health_check_detailed():
    return {
        "status": "healthy",
        "service": "syllaai-backend",
        "database": "healthy",
    }

@app.get("/")
async def root():
    return {"message": "SyllabAI Backend API", "status": "operational"}

# ------------------------------------------------------------------ #
#  Routers
# ------------------------------------------------------------------ #
# mount all routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(events.router,  prefix="/api")


# ------------------------------------------------------------------ #
#  Local dev entry-point
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
