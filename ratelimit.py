"""Small in-memory rate limiter for the scan and account forms.

Each server process keeps its own counts, so on Vercel (many short-lived
processes) this is a speed bump rather than a hard guarantee. It still stops a
single visitor from hammering one instance with scans, which is where the cost
is: every scan runs GrabCut and the SVM.
"""
import time
import threading
from collections import defaultdict, deque

from flask import request

_hits = defaultdict(deque)
_lock = threading.Lock()


def client_ip():
    # ProxyFix (enabled on Vercel) has already moved the real client into remote_addr
    return request.remote_addr or "unknown"


def allow(bucket, limit, window_seconds):
    """Record one hit for this client in `bucket`; False once `limit` hits fall inside the window."""
    key = (bucket, client_ip())
    now = time.monotonic()
    with _lock:
        hits = _hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        # Drop idle keys now and then so memory stays flat
        if len(_hits) > 5000:
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > window_seconds]:
                del _hits[k]
        return True
