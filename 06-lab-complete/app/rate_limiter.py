import time
from collections import defaultdict, deque
from fastapi import HTTPException, status
from app.config import settings

class SlidingWindowRateLimiter:
    def __init__(self, window_size_seconds: int = 60):
        self.window_size = window_size_seconds
        # Maps user/IP keys to a deque of timestamps
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    def check_limit(self, key: str) -> None:
        now = time.time()
        user_window = self._windows[key]

        # 1. Clear out timestamps older than the sliding window (e.g., 60s)
        while user_window and user_window[0] < now - self.window_size:
            user_window.popleft()

        # 2. Check if the user has hit their max requests
        if len(user_window) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min.",
                headers={"Retry-After": str(self.window_size)},
            )

        # 3. Record the current request timestamp
        user_window.append(now)

# Instantiate a single tracker to be imported throughout your app
limiter = SlidingWindowRateLimiter()