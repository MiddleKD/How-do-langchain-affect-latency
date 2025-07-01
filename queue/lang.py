from fastapi import FastAPI
from pydantic import BaseModel
from tasks_lang import run_chain_task, app as celery_app
from celery.result import AsyncResult

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(request: GenerateRequest):
    task = run_chain_task.delay(request.prompt)  # Celery 백그라운드 작업 실행
    return {"task_id": task.id}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "pending"}

    if result.state == "SUCCESS":
        return {"status": "completed", "result": result.result}

    if result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}

    return {"status": result.state}
