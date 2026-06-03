from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Custom exception classes
# ---------------------------------------------------------------------------


class AppException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, detail: str, status_code: int = 500) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(AppException):
    """Resource not found — maps to HTTP 404."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404)


class UnauthorizedException(AppException):
    """Authentication required or failed — maps to HTTP 401."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(detail=detail, status_code=401)


class ForbiddenException(AppException):
    """Insufficient permissions — maps to HTTP 403."""

    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(detail=detail, status_code=403)


class BadRequestException(AppException):
    """Invalid client request — maps to HTTP 400."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(detail=detail, status_code=400)


class ConflictException(AppException):
    """Resource conflict (e.g. duplicate) — maps to HTTP 409."""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(detail=detail, status_code=409)


# ---------------------------------------------------------------------------
# Exception handlers to register with the FastAPI application
# ---------------------------------------------------------------------------


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all custom AppException subclasses with a uniform JSON body."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": type(exc).__name__,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app instance.

    Call this during app startup:

        from app.core.exceptions import register_exception_handlers
        register_exception_handlers(app)
    """
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
