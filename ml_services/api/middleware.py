"""
API Middleware
==============

Custom middleware for logging, error handling, and performance monitoring.
"""

import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logger import get_logger
from ..utils.metrics import metrics

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Record metrics
            metrics.record_request(
                endpoint=request.url.path,
                response_time=process_time,
                status_code=response.status_code
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Record error
            metrics.record_request(
                endpoint=request.url.path,
                response_time=process_time,
                status_code=500
            )
            
            # Log error
            logger.error(
                f"Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time,
                },
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "detail": str(e) if logger.level <= 10 else None  # Only in DEBUG
                }
            )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "ValidationError",
                    "message": str(e)
                }
            )
        except FileNotFoundError as e:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "NotFound",
                    "message": str(e)
                }
            )
        except Exception as e:
            logger.exception("Unhandled exception in middleware")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred"
                }
            )
