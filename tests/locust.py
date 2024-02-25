import random

from locust import HttpUser, between, task


class GatewayUser(HttpUser):

    wait_time = between(1, 2)

    @task
    def test_post(self):
        self.client.post("/", json={"name": "World", 'salt': str(random.randint(1, 10_000))})
