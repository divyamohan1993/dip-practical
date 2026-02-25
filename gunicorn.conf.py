"""Gunicorn configuration for production deployment."""
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/dip-practical/access.log"
errorlog = "/var/log/dip-practical/error.log"
loglevel = "info"
