import multiprocessing

worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count()
bind = "0.0.0.0:18008"
timeout = 90
keepalive = 3600
preload_app = True
