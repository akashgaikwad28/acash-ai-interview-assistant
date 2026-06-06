"""Rate limiting setup for public API routes.

Purpose:
    Protect public endpoints from excessive request volume.
Responsibilities:
    Create and expose the SlowAPI limiter configured by client IP address.
Dependencies:
    slowapi.
Usage:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, ...)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)
