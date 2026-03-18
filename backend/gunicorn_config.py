"""
Gunicorn Configuration for Production

Optimized for concurrent request handling with threads + workers.
This prevents worker blocking when using ThreadPoolExecutor for parallel AI calls.

Worker/thread count is configurable via environment variables to support
different deployment targets (VPS with limited RAM vs larger instances).

Default: 2 workers × 2 threads = 4 concurrent requests (fits 4GB VPS)
Override: Set GUNICORN_WORKERS and GUNICORN_THREADS env vars for more capacity.
"""

import multiprocessing
import os

# Number of worker processes
# Default 2 for VPS deployments (each worker loads spaCy model ~200MB)
# Override with GUNICORN_WORKERS env var for larger instances
workers = int(os.getenv('GUNICORN_WORKERS', 2))

# Number of threads per worker
# Default 2 for VPS, override with GUNICORN_THREADS for more concurrency
threads = int(os.getenv('GUNICORN_THREADS', 2))

# Worker class - use gthread for proper thread support
worker_class = "gthread"

# Timeout for requests (in seconds)
# AI analysis can take 30-60 seconds, so 120s gives buffer
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# Keep-alive timeout
keepalive = 5

# Bind address
bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# Process naming
proc_name = "resumatch-api"

# Worker connections (max simultaneous clients per worker)
worker_connections = 1000

# Preload app for better memory usage (shared across workers)
preload_app = True

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Maximum requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50







