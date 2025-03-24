# gunicorn.conf.py

# Number of worker processes
workers = 4

# Timeout for workers (in seconds)
timeout = 120

# Maximum number of requests a worker will process before restarting
max_requests = 1000

# Logging configuration
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stdout
loglevel = 'info'

# Preload the application before the worker processes are forked
preload_app = True

# Worker class (for async support)
worker_class = 'sync'  # or 'gevent' if you need async support

# Bind to a socket
bind = '0.0.0.0:8000'