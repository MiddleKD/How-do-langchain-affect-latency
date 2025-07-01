from locust import HttpUser, task, between
import time

class CeleryLoadTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def generate_and_poll(self):
        start_time = time.time()

        # 1) /generate 요청 성공/실패 관리
        with self.client.post("/generate", json={"prompt": "Tell me a short joke"}, catch_response=True) as generate_response:
            if generate_response.status_code != 200:
                generate_response.failure(f"Generate API failed: {generate_response.status_code}")
                return

            try:
                task_id = generate_response.json().get("task_id")
            except Exception as e:
                generate_response.failure(f"Invalid JSON response: {str(e)}")
                return

            if not task_id:
                generate_response.failure("No task_id returned")
                return

            # /generate 요청은 성공으로 표시
            generate_response.success()

        # 2) /result/{task_id} 폴링 처리 — 별도 context manager 사용
        max_wait_time = 30
        poll_interval = 2
        total_wait = 0
        while total_wait < max_wait_time:
            with self.client.get(f"/result/{task_id}", catch_response=True) as result_response:
                if result_response.status_code != 200:
                    result_response.failure(f"Polling API error: {result_response.status_code}")
                    return

                try:
                    result_json = result_response.json()
                except Exception as e:
                    result_response.failure(f"Invalid result JSON: {str(e)}")
                    return

                status = result_json.get("status")

                if status == "completed":
                    result_response.success()
                    break
                elif status == "failed":
                    result_response.failure(f"Task failed: {result_json.get('error')}")
                    return

            time.sleep(poll_interval)
            total_wait += poll_interval
        else:
            # timeout 폴링 실패는 별도 로깅 혹은 실패 처리 필요
            self.environment.events.request.fire(
                request_type="GET",
                name="/result/{task_id} polling",
                response_time=total_wait * 1000,
                response_length=0,
                exception=Exception(f"Timeout waiting for task completion after {max_wait_time} seconds"),
                context=None,
                response=None,
                type="failure"
            )
            return

        end_time = time.time()

        # 전체 처리 시간 기록 (generate + poll)
        self.environment.events.request.fire(
            request_type="POST+GET(s)",
            name="/generate + /result polling",
            response_time=(end_time - start_time)*1000,
            response_length=0,
            exception=None,
            context=None,
            response=None,
            type="success"
        )
