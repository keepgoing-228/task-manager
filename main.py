import os
import shutil
import subprocess
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

# FastAPI app
app = FastAPI(title="Task Manager")
# thread pool
executor = ThreadPoolExecutor(max_workers=1)
jobs: dict[str, Future] = {}  # job_id -> future


# this is the request body for the POST /tasks endpoint
class TaskRequest(BaseModel):
    cmd: str


class FileUploadResponse(BaseModel):
    message: str
    filename: str
    file_path: str
    file_size: int


def run_task(cmd: str) -> str:
    """
    execute a single command.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {cmd}")
    subprocess.run(cmd, shell=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Finished: {cmd}")
    return cmd


@app.post("/tasks/upload", status_code=202)
def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """
    upload a file to the server.
    """
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        return FileUploadResponse(
            message=f"File '{file.filename}' uploaded successfully",
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.post("/tasks/", status_code=202)  # 202 means accepted, the task is being processed
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
def list_jobs() -> dict:
    """
    list all jobs.
    """
    return {
        "jobs": [
            {
                "job_id": job_id,
                "done": future.done(),
                "cmd_done": future.result() if future.done() else None,
            }
            for job_id, future in jobs.items()
        ]
    }


@app.get("/list_files")
def list_uploaded_files() -> dict:
    """
    list all uploaded files.
    """
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        return {"files": []}

    files = []
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            files.append(
                {
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path),
                    "modified_time": time.ctime(os.path.getmtime(file_path)),
                }
            )

    return {"files": files}
