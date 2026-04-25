import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.core.logger import get_logger


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info(f"Incoming request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            duration_ms = round((time.time() - start_time) * 1000, 2)

            logger.info(
                f"Completed request: {request.method} {request.url.path} "
                f"status={response.status_code} duration_ms={duration_ms}"
            )

            return response

        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)

            logger.exception(
                f"Request failed: {request.method} {request.url.path} "
                f"duration_ms={duration_ms} error={str(exc)}"
            )

            raise exc