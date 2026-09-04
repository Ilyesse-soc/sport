from collections import defaultdict, deque
from threading import Lock
from time import time
import os
from fastapi import HTTPException, Request, status


_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
_LOCK = Lock()


LIMITS = {
    "auth": (5, 60),
    "api": (100, 60),
    "upload": (10, 60),
    "ai": (10, 60),
    "ai_photo": (5, 60),
}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_rate_limit(request: Request, category: str, user_key: str | None = None) -> None:
    if os.getenv("TESTING") == "1":
        return
    limit, window_sec = LIMITS[category]
    ip = _client_ip(request)
    identity = user_key or request.headers.get("authorization", "anon")[:64]
    key = f"{category}:{ip}:{identity}"
    now = time()

    with _LOCK:
        bucket = _BUCKETS[key]
        while bucket and bucket[0] <= now - window_sec:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        bucket.append(now)
