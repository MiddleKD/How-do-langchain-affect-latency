from fastapi import FastAPI
from pydantic import BaseModel, Field
import time
import httpx  # 비동기 HTTP 클라이언트

app = FastAPI()

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

client = httpx.AsyncClient()

class GenerateRequest(BaseModel):
    prompt: str = Field("Tell me a short joke", description="Input text")

# Tool 역할 (async)
async def dummy_tool(input_text):
    payload = {
        "model": MODEL_NAME,
        "prompt": input_text,
        "stream": False
    }
    start_time = time.time()
    response = await client.post(OLLAMA_API_URL, json=payload, timeout=60)
    elapsed = time.time() - start_time

    if response.status_code == 200:
        content = response.json().get("response", "")
        return content
    else:
        raise Exception(f"Ollama API Error: {response.status_code} - {response.text}")

# First Chain (async)
async def first_chain(input_text):
    tool_output = await dummy_tool(input_text)
    return tool_output

# Second Chain (async)
async def second_chain(tool_result):
    return f"[Final Response] {tool_result}"

@app.post("/generate")
async def generate(request: GenerateRequest):
    start_time = time.time()

    tool_output = await first_chain(request.prompt)
    final_output = await second_chain(tool_output)

    total_time = time.time() - start_time

    return {
        "output": final_output,
        "elapsed_time_sec": total_time
    }