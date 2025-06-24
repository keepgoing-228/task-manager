import os
import shutil
import subprocess
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

# FastAPI app
app = FastAPI(title="Task Manager")


@dataclass
class JobInfo:
    future: Future
    filename: str
    file_size: int
    language: str


# thread pool
executor = ThreadPoolExecutor(max_workers=1)
jobs: dict[str, JobInfo] = {}  # job_id -> JobInfo
# upload directory
UPLOAD_DIR = Path("uploads")


def run_reading_txt_task(file_path: Path, language: str = "english") -> Path:
    """
    execute a single command.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {file_path} with language: {language}")
    subprocess.run(["python", "read_txt.py", f"{file_path}", f"{language}"])
    # subprocess.run(f"python read_txt.py {file_path} {language}", shell=True)
    # cmd = "/home/wesley/GitHub/ASRtranslate/.venv/bin/python -m asrtranslate {} -l {}".split(" ")
    # subprocess.run(
    #     [
    #         "python",
    #         "-m",
    #         "asrtranslate",
    #         "   r  r",
    #         "-l",
    #     ],
    # )
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


@app.post("/tasks/{language}")
def upload_and_run(language: str, file: UploadFile = File(...)) -> dict:
    """
    upload a file to the server and run the task with specified language.
    It will return message, filename, file_path, file_size, job_id, language.
    """
    try:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR, exist_ok=True)

        assert file.filename

        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        # submit the task
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobInfo(
            future=executor.submit(run_reading_txt_task, file_path, language),
            filename=file.filename,  # pyright: ignore[reportArgumentType]
            file_size=file_size,
            language=language,
        )

        return {
            "message": f"File '{file.filename}' uploaded and task started successfully with language: {language}",
            "job_id": job_id,
            "filename": file.filename,
            "file_size": file_size,
            "language": language,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"File upload or task start failed: {str(e)}"
        )


@app.get("/tasks/status/{job_id}")
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
        "file_size": job_info.file_size,
        "language": job_info.language,
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
                "file_size": job_info.file_size,
                "language": job_info.language,
            }
            for job_id, job_info in jobs.items()
        ]
    }


@app.get("/list_files")
def list_uploaded_files() -> dict:
    """
    list all uploaded files.
    """
    if not UPLOAD_DIR.exists():
        return {"files": []}

    files = []
    for entry in UPLOAD_DIR.iterdir():
        if entry.is_file():
            files.append(
                {
                    "filename": entry.name,
                    "file_size": entry.stat().st_size,
                    "modified_time": entry.stat().st_mtime,
                }
            )

    return {"files": files}
