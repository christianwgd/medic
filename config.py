bind = '0.0.0.0:8000'
backlog = 2048
proc_name = 'medic'
restart = True
deamon = True

workers = 1
worker_class = 'sync'
timeout = 30
keepalive = 2

errorlog = '-'
accesslog = '-'
