"""
Custom middleware for the API
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response information.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        client_host = request.client.host if request.client else 'unknown'
        logger.info(
            "Request started - id: {}, method: {}, path: {}, client: {}",
            request_id,
            request.method,
            request.url.path,
            client_host
        )

        start_time = time.time()

        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = (time.time() - start_time) * 1000

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

            # Log response
            logger.info(
                "Request completed - id: {}, status: {}, time: {:.2f}ms",
                request_id,
                response.status_code,
                process_time
            )

            return response

        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "Request failed - id: {}, time: {:.2f}ms, error: {}",
                request_id,
                process_time,
                repr(e),
                exc_info=True
            )
            raise


class CORSMiddleware:
    """
    Note: FastAPI has built-in CORS middleware.
    This is just a placeholder for custom CORS logic if needed.
    """
    pass