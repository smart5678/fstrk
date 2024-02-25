import json

import requests

from project import settings
from project.celery_app import app


@app.task(bind=True, rate_limit='8/s')
def proxy_request(self, body: dict, headers: dict):
    if settings.DEBUG:
        headers['X-Celery-ID'] = self.request.id
    resp = requests.post(settings.RECEIVER_URL, data=json.dumps(body), headers=headers)
    return resp.status_code
