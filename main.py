import subprocess
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI app
app = FastAPI(title="Task Manager")
# thread pool
executor = ThreadPoolExecutor(max_workers=1)
jobs: dict[str, Future] = {}


# this is the request body for the POST /tasks endpoint
class TaskRequest(BaseModel):
    cmd: str


def run_task(cmd: str) -> str:
    """
    execute a single command.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {cmd}")
    subprocess.run(cmd, shell=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Finished: {cmd}")
    return cmd


@app.post("/tasks/", status_code=202)
def add_task(request: TaskRequest) -> dict:
    """
    add a task to the thread pool.
    """
    job_id = str(uuid.uuid4())
    future = executor.submit(run_task, request.cmd)
    jobs[job_id] = future
    return {"job_id": job_id, "cmd": request.cmd}


@app.get("/tasks/{job_id}")
def get_task_status(job_id: str) -> dict:
    """
    get the status of a task.
    """
    future = jobs.get(job_id)
    if future is None:
        return {"job_id": job_id, "done": False}
    return {
        "job_id": job_id,
        "done": future.done(),
        "cmd_done": future.result() if future.done() else None,
    }


@app.get("/tasks/")
def list_jobs() -> list[dict]:
    """
    list all jobs.
    """
    return [
        {
            "job_id": job_id,
            "done": future.done(),
            "cmd_done": future.result() if future.done() else None,
        }
        for job_id, future in jobs.items()
    ]
