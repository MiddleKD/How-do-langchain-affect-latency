from celery import Celery
import httpx
import time

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

class DummyTool:
    def invoke(self, input_text: str) -> str:
        payload = {
            "model": MODEL_NAME,
            "prompt": input_text,
            "stream": False
        }
        start_time = time.time()
        response = httpx.post(OLLAMA_API_URL, json=payload, timeout=60)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            content = response.json().get("response", "")
            return content
        else:
            raise Exception(f"Ollama API Error: {response.status_code} - {response.text}")

class FirstChain:
    def invoke(self, input_text: str) -> str:
        tool = DummyTool()
        return tool.invoke(input_text)

class SecondChain:
    def invoke(self, tool_result: str) -> str:
        return f"[Final Response] {tool_result}"

first_chain = FirstChain()
second_chain = SecondChain()

@app.task
def run_chain_task(prompt: str) -> str:
    tool_output = first_chain.invoke(prompt)
    final_output = second_chain.invoke(tool_output)
    return final_output
