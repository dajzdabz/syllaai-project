from starlette import status


class AppException(Exception):
    """Base class: every custom error has an HTTP status and a detail string."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal Server Error"

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class BadRequest(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"


class Unauthorized(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized"


class Forbidden(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"


class NotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"


class Conflict(AppException):  # e.g. unique-key violations
    status_code = status.HTTP_409_CONFLICT
    detail = "Conflict"
