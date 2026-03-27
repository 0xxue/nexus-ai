"""Global error handlers - consistent JSON error responses."""

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = structlog.get_logger()


def register_error_handlers(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        trace_id = getattr(request.state, "trace_id", "unknown")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "trace_id": trace_id, "status": exc.status_code},
        )

    @app.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        trace_id = getattr(request.state, "trace_id", "unknown")
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "trace_id": trace_id, "status": 400},
        )

    @app.exception_handler(Exception)
    async def general_error(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", "unknown")
        logger.error("Unhandled error", trace_id=trace_id, error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "trace_id": trace_id, "status": 500},
        )
