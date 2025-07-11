import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from psycopg2.errors import UniqueViolation  # Postgres-specific
from app.exceptions import AppException, BadRequest, Conflict


log = logging.getLogger("syllaai.errors")


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        # ---------- OUR CUSTOM EXCEPTIONS ----------
        except AppException as exc:
            return _json(exc.status_code, exc.detail)

        # ---------- Pydantic & validation ----------
        except ValidationError as exc:
            return _json(422, exc.errors())

        # ---------- DB integrity / unique key ----------
        except IntegrityError as exc:
            # dig into PG error code to distinguish unique-key vs other
            if isinstance(exc.orig, UniqueViolation):
                return _json(409, "Resource already exists")
            raise  # let outer handler convert to 500

        # ---------- Fallback ----------
        except Exception as exc:
            log.exception("Unhandled error on %s %s", request.method, request.url.path)
            return _json(500, "Internal Server Error")


def _json(status_code: int, detail):
    return JSONResponse(status_code=status_code, content={"detail": detail})
