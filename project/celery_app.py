import os
import sys

from celery import Celery

this_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(this_file_dir, '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery(__name__)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['gateway'], related_name='tasks')
