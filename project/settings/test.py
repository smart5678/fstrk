from gateway.tasks import proxy_request
from project.celery_app import app
from project.settings.__init__ import *  # NOQA

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test',
    }
}

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

app.tasks.register(proxy_request)
