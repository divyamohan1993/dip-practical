"""Gunicorn configuration for Cloud Run deployment.

Cloud Run requires the container to listen on 0.0.0.0:$PORT (default 8080)
and log to stdout/stderr (Cloud Logging picks them up automatically).
The VM deployment uses the separate gunicorn.conf.py which binds to
127.0.0.1:8000 and logs to files for nginx + systemd.
"""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 2
threads = 8
worker_class = "gthread"
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 500
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
