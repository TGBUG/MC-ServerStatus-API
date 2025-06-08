import time

class RateLimiter:
    def __init__(self, limit, interval=60):
        self.limit = limit
        self.interval = interval
        self.history = []

    def allow(self):
        now = time.time()
        self.history = [t for t in self.history if now - t < self.interval]
        if len(self.history) >= self.limit:
            return False
        self.history.append(now)
        return True

global_limiter = RateLimiter(limit=60)
