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
# upload directory
UPLOAD_DIR = "uploads"


# this is the request body for the POST /tasks endpoint
class TaskRequest(BaseModel):
    file_path: str


class FileUploadResponse(BaseModel):
    message: str
    filename: str
    file_path: str
    file_size: int


def run_task(file_path: str) -> str:
    """
    execute a single command.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {file_path}")
    subprocess.run(f"python read_txt.py {file_path}", shell=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Finished: {file_path}")
    return file_path


@app.post("/tasks/", status_code=202)
def upload_and_run(file: UploadFile = File(...)) -> dict:
    """
    upload a file to the server and run the task.
    """
    try:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR, exist_ok=True)

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        # submit the task
        job_id = str(uuid.uuid4())
        future = executor.submit(run_task, file_path)
        jobs[job_id] = future

        return {
            "message": f"File '{file.filename}' uploaded and task started successfully",
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "job_id": job_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"File upload or task start failed: {str(e)}"
        )


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
            }
            for job_id, future in jobs.items()
        ]
    }


@app.get("/list_files")
def list_uploaded_files() -> dict:
    """
    list all uploaded files.
    """
    if not os.path.exists(UPLOAD_DIR):
        return {"files": []}

    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
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
