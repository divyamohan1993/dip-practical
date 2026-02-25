"""Gunicorn configuration for production deployment.

Tuned for e2-medium (2 vCPU, 4 GB RAM) serving 200+ concurrent users.
Using gthread workers: each worker handles many requests via threads.
Matplotlib with Agg backend is thread-safe when using fig-scoped methods
(fig.tight_layout, fig.savefig, fig.colorbar) instead of plt globals.
"""
bind = "127.0.0.1:8000"
workers = 2                # 1 per vCPU — keeps memory reasonable
threads = 8                # 8 threads per worker = 16 concurrent requests
worker_class = "gthread"   # threaded workers for I/O + CPU mix
timeout = 120              # matplotlib plots can take a few seconds
graceful_timeout = 30
keepalive = 5
max_requests = 500         # recycle workers to prevent memory leaks
max_requests_jitter = 50   # stagger restarts so not all workers recycle at once
accesslog = "/var/log/dip-practical/access.log"
errorlog = "/var/log/dip-practical/error.log"
loglevel = "info"
