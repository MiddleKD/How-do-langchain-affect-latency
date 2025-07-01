from celery import Celery
from langchain_core.runnables import Runnable
from langchain_ollama.chat_models import ChatOllama

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

llm = ChatOllama(model="llama3.1")

class DummyTool(Runnable):
    def invoke(self, input_text):
        response = llm.invoke(input_text)
        return response.content

class FirstChain(Runnable):
    def invoke(self, input_text):
        tool = DummyTool()
        return tool.invoke(input_text)

class SecondChain(Runnable):
    def invoke(self, tool_result):
        return f"[Final Response] {tool_result}"

first_chain = FirstChain()
second_chain = SecondChain()

@app.task
def run_chain_task(prompt: str):
    tool_output = first_chain.invoke(prompt)
    final_output = second_chain.invoke(tool_output)
    return final_output
