from fastapi import FastAPI
from pydantic import BaseModel
import time
from langchain_core.runnables import Runnable
from langchain_ollama.chat_models import ChatOllama

app = FastAPI()

llm = ChatOllama(model="llama3.1")

class GenerateRequest(BaseModel):
    prompt: str

# Tool 역할
class DummyTool(Runnable):
    async def invoke(self, input_text):
        response = await llm.ainvoke(input_text)
        return response.content

# First Chain
class FirstChain(Runnable):
    async def invoke(self, input_text):
        tool = DummyTool()
        return await tool.invoke(input_text)

# Second Chain
class SecondChain(Runnable):
    async def invoke(self, tool_result):
        return f"[Final Response] {tool_result}"

first_chain = FirstChain()
second_chain = SecondChain()

@app.post("/generate")
async def generate(request: GenerateRequest):
    start_time = time.time()

    tool_output = await first_chain.invoke(request.prompt)
    final_output = await second_chain.invoke(tool_output)

    elapsed = time.time() - start_time

    return {
        "output": final_output,
        "elapsed_time_sec": elapsed
    }
