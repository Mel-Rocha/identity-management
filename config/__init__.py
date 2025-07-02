from __future__ import absolute_import, unicode_literals

# Isso garante que o Celery seja carregado ao iniciar o Django
from config.celery import app as celery_app

__all__ = ('celery_app',)
