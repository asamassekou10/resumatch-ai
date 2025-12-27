"""
Gunicorn Configuration for Production

Optimized for concurrent request handling with threads + workers.
This prevents worker blocking when using ThreadPoolExecutor for parallel AI calls.

Configuration:
- 4 workers × 4 threads = 16 concurrent requests
- 120 second timeout (sufficient for AI analysis)
- gthread worker class for proper thread support
"""

import multiprocessing
import os

# Number of worker processes
# Use 4 workers for good balance (can handle 16 concurrent requests with threads)
workers = int(os.getenv('GUNICORN_WORKERS', 4))

# Number of threads per worker
# 4 threads per worker = 4 workers × 4 threads = 16 concurrent requests
threads = int(os.getenv('GUNICORN_THREADS', 4))

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





