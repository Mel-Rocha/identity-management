import os
import django

from decouple import config as config_

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

bind = f"[::]:{config_('PORT', default='8000')}"
workers = 2
threads = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 10000

# Configuração de logs
loglevel = 'info'
accesslog = '/var/log/access.log'
errorlog  = '/var/log/error.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


def post_fork(server, worker):
    pass
