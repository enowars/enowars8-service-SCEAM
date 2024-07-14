import multiprocessing

worker_class = "gthread"
threads = 4
workers = min(6, multiprocessing.cpu_count())
bind = "0.0.0.0:8008"
timeout = 90
keepalive = 3600
preload_app = True
