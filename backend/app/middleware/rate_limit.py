"""
Rate limiting middleware for API protection
"""
import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.limits = {
            "default": (100, 60),  # 100 requests per 60 seconds
            "chat": (30, 60),     # 30 chat requests per 60 seconds
            "translate": (50, 60),  # 50 translation requests per 60 seconds
            "voice": (20, 60),     # 20 voice requests per 60 seconds
        }
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP + optional user agent hash)."""
        client_ip = request.client.host if request.client else "unknown"
        return client_ip
    
    def _clean_old_requests(self, client_id: str, window: int):
        """Remove requests outside the time window."""
        now = time.time()
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
    
    def is_rate_limited(self, request: Request, endpoint: str = "default") -> Tuple[bool, dict]:
        """
        Check if request should be rate limited.
        Returns (is_limited, headers_dict).
        """
        client_id = self._get_client_id(request)
        limit, window = self.limits.get(endpoint, self.limits["default"])
        
        # Clean old requests
        self._clean_old_requests(client_id, window)
        
        # Count requests in window
        request_count = len(self.requests[client_id])
        
        # Check if limit exceeded
        if request_count >= limit:
            return True, {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + window)),
                "Retry-After": str(window),
            }
        
        # Record this request
        self.requests[client_id].append(time.time())
        
        return False, {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(limit - request_count - 1),
            "X-RateLimit-Reset": str(int(time.time() + window)),
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Middleware for rate limiting."""
    # Determine endpoint type from path
    path = request.url.path
    endpoint = "default"
    
    if "/chat" in path:
        endpoint = "chat"
    elif "/translate" in path:
        endpoint = "translate"
    elif "/voice" in path or "/ws" in path:
        endpoint = "voice"
    
    # Check rate limit
    is_limited, headers = rate_limiter.is_rate_limited(request, endpoint)
    
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": headers.get("Retry-After", 60),
            },
            headers=headers,
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    for key, value in headers.items():
        response.headers[key] = value
    
    return response
