import os
import shutil
import subprocess
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

# FastAPI app
app = FastAPI(title="Task Manager")


@dataclass
class JobInfo:
    future: Future
    filename: str
    file_path: str
    file_size: int


# thread pool
executor = ThreadPoolExecutor(max_workers=1)
jobs: dict[str, JobInfo] = {}  # job_id -> JobInfo
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


def run_reading_txt_task(file_path: str) -> str:
    """
    execute a single command.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {file_path}")
    subprocess.run(f"python read_txt.py {file_path}", shell=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Finished: {file_path}")
    return file_path


def check_task_status(job_id: str) -> str:
    """
    check the status of a task. Status can be:
    - "pending": the task is pending
    - "running": the task is running
    - "done": the task is done
    - "failed": the task failed
    """
    job_info = jobs.get(job_id)
    if job_info is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job_info.future.running():
        return "running"
    if job_info.future.done():
        try:
            job_info.future.result()
            return "done"
        except Exception as e:
            return "failed"
    return "pending"


@app.post("/tasks/", status_code=202)
def upload_and_run(file: UploadFile = File(...)) -> dict:
    """
    upload a file to the server and run the task.
    It will return message, filename, file_path, file_size, job_id.
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
        future = executor.submit(run_reading_txt_task, file_path)
        jobs[job_id] = JobInfo(
            future=future,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
        )

        return {
            "message": f"File '{file.filename}' uploaded and task started successfully",
            "job_id": job_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"File upload or task start failed: {str(e)}"
        )


@app.get("/tasks/{job_id}")
def get_task_status(job_id: str) -> dict:
    """
    get the status of a task.
    It will return job_id, status and file information.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job_info = jobs[job_id]
    return {
        "job_id": job_id,
        "status": check_task_status(job_id),
        "filename": job_info.filename,
        "file_path": job_info.file_path,
        "file_size": job_info.file_size,
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
                "status": check_task_status(job_id),
                "filename": job_info.filename,
                "file_path": job_info.file_path,
                "file_size": job_info.file_size,
            }
            for job_id, job_info in jobs.items()
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
