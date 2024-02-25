import time
import uuid

import pytest
from celery.result import AsyncResult
from mock import patch
from rest_framework.reverse import reverse

from .test_http_server import test_http_server  # NOQA


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def request_data():
    data = {
        'value': 'content'
    }
    return data


@pytest.fixture
def request_random_data():
    def make_data():
        data = {
           'value': 'content ' + str(uuid.uuid4())
        }
        return data
    return make_data


@pytest.fixture
def enable_debug(settings):
    settings.DEBUG = True


@pytest.mark.usefixtures("celery_app", "celery_worker")
def test_simple_post(api_client, request_random_data):
    url = reverse('gateway')
    response = api_client.post(url, data=request_random_data())
    assert response.status_code == 200
    assert 'X-Celery-ID' not in response.headers


@pytest.mark.usefixtures('celery_worker')
@patch(
    'gateway.tasks.proxy_request.apply_async',
    return_value=type('FakeTask', (), {'id': 'patched_id'})
)
def test_headers_in_debug(patched_task, api_client, request_random_data, enable_debug):
    url = reverse('gateway')
    response = api_client.post(url, data=request_random_data())
    assert 'X-Celery-ID' in response.headers
    assert patched_task.call_count == 1
    assert response.headers['X-Celery-ID'] == 'patched_id'


@pytest.mark.usefixtures('celery_worker', 'test_http_server')
def test_headers_task_success(api_client, request_random_data, enable_debug):
    url = reverse('gateway')
    response = api_client.post(url, data=request_random_data())
    res = AsyncResult(response.headers['X-Celery-ID'])
    while not res.ready():
        time.sleep(0.1)
    assert 'X-Celery-ID' in response.headers
    assert res.result == 200
    assert res.status == 'SUCCESS'


@pytest.mark.usefixtures('celery_worker')
@patch(
    'gateway.tasks.proxy_request.apply_async',
    return_value=type('FakeTask', (), {'id': 'patched_id'})
)
def test_deduplicate(patched_task, api_client, request_data, enable_debug):
    """
    Вызовется только 2 таска на пердачу запроса.
    Первый из дублирующихся. И последний с другим телом
    """
    url = reverse('gateway')
    api_client.post(url, data=request_data)
    api_client.post(url, data=request_data)
    api_client.post(url, data=request_data)
    api_client.post(url, data={'value': 'content 1'})
    assert patched_task.call_count == 2


@pytest.mark.usefixtures('celery_worker')
@patch(
    'gateway.tasks.proxy_request.apply_async',
    return_value=type('FakeTask', (), {'id': 'patched_id'})
)
def test_random_requests(patched_task, api_client, request_random_data, enable_debug):
    url = reverse('gateway')
    results = []
    for _ in range(100):
        results.append(api_client.post(url, data=request_random_data()))
    assert patched_task.call_count == 100
    assert all(result.status_code == 200 for result in results)


@pytest.mark.usefixtures('celery_worker', 'test_http_server')
def test_throttling(api_client, request_random_data, enable_debug):
    """C 8RPS на отправку 10 запросов как минимум будут выполняться дольше секунды"""
    url = reverse('gateway')
    results = []
    for _ in range(10):
        response = api_client.post(url, data=request_random_data())
        results.append(AsyncResult(response.headers['X-Celery-ID']))

    while not all(result.ready() for result in results):
        time.sleep(0.1)
    ordered_results = sorted(results, key=lambda r: r.date_done, reverse=True)
    assert bool((ordered_results[0].date_done - ordered_results[-1].date_done).seconds > 1)
