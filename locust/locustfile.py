from locust import HttpUser, task, between

class OllamaLoadTestUser(HttpUser):
    wait_time = between(1, 2)  # 요청 간 대기 시간 (초)

    @task
    def generate_text(self):
        payload = {
            "prompt": "Tell me a short joke"
        }
        with self.client.post("/generate", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status {response.status_code}")
            else:
                response.success()
