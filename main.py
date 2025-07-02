import os
import shutil
import subprocess
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import urllib.parse

from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.staticfiles import StaticFiles

from smtp_email import EmailSender

WORK_DIR = Path("/home/wesley/GitHub/ASRtranslate")
UPLOAD_DIR = WORK_DIR / "uploads"
RESULT_DIR = WORK_DIR / "results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Task Manager")
app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

# FastAPI configuration
FASTAPI_SERVER = "192.168.40.70"
FASTAPI_PORT = 3030
EMAIL_SENDER_ACCOUNT = "r10631039@g.ntu.edu.tw"


@dataclass
class JobInfo:
    future: Future
    filename: str
    file_size: int
    language: str
    email: str | None = None  # 新增 email 欄位
    # language_list: list[dict[str(language_name), str(status)]]


class Language(StrEnum):
    EN = "en"
    TW = "tw"
    CN = "cn"
    JP = "jp"
    KO = "ko"
    DE = "de"
    FR = "fr"
    ES = "es"

    __fullname = {
        EN: "english",
        TW: "traditional chinese",
        CN: "simplified chinese",
        JP: "japanese",
        KO: "korean",
        DE: "german",
        FR: "french",
        ES: "spanish",
    }

    def fullname(self) -> str:
        return self.__fullname[self]

    @classmethod
    def from_fullname(cls, fullname: str) -> str:
        """Convert full language name to short code"""
        fullname_lower = fullname.lower()
        for code, name in cls.__fullname.items():
            if name.lower() == fullname_lower:
                return code
        # If not found, return the original string
        return fullname


# thread pool
executor = ThreadPoolExecutor(max_workers=1)
jobs: dict[str, JobInfo] = {}  # job_id -> JobInfo


def run_translation_task(
    original_file_path: Path, language: list[str] = ["en"], email: str | None = None
):
    """
    execute a single command.
    """
    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running: {original_file_path} with language: {language}"
    )

    generated_files = []

    for lang in language:
        cmd = [
            WORK_DIR / ".venv/bin/python",
            "-m",
            "asrtranslate",
            f"{original_file_path}",
            "-o",
            f"{RESULT_DIR}",
            "-l",
            f"{lang}",
        ]

        p = subprocess.Popen(cmd, cwd=WORK_DIR)
        print(f"pid: {p.pid}")

        return_code = p.wait()
        if return_code != 0:
            raise Exception(f"Translation failed with return code: {return_code}")

        # check if the generated file exists
        # TODO: not sync with the translation process
        original_name = original_file_path.stem
        generated_file = RESULT_DIR / f"{original_name}-{lang}.idml"
        if generated_file.exists():
            generated_files.append(generated_file)

        ## TODO: add a way to stop the task
        # while p.poll() is None:
        #     if is_stop:
        #         p.terminate()
        #     sleep(0.5)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Finished: {original_file_path}")

    if email and generated_files:
        send_completion_email(email, original_file_path.name, generated_files, language)


def send_completion_email(
    email: str,
    original_filename: str,
    generated_files: list[Path],
    languages: list[str],
):
    """
    send email notification when the task is completed
    """
    try:
        email_sender = EmailSender()

        # create download links
        download_links = []
        for file_path in generated_files:
            filename = file_path.name
            download_url = f"http://{FASTAPI_SERVER}:{FASTAPI_PORT}/results/{urllib.parse.quote(filename)}"
            download_links.append(download_url)

        # create email content
        subject = f"ASRtranslate 翻譯完成 - {original_filename}"

        message = f"""
您的檔案翻譯已完成！

原始檔案: {original_filename}
翻譯語言: {', '.join(languages)}

下載連結:
{"\n".join(download_links)}

請點擊上方連結下載翻譯後的檔案。

---
ASRtranslate,
ASRock AI Team
        """.strip()

        success = email_sender.send_email(
            sender=EMAIL_SENDER_ACCOUNT,
            recipients=[email],
            subject=subject,
            message=message,
            domain="",
            password=os.getenv("PASSWORD"),
            use_ntlm=False,
            include_timestamp=True,
        )

        if success:
            print(f"Email notification sent to {email}")
        else:
            print(f"Failed to send email notification to {email}")

    except Exception as e:
        print(f"Error sending email notification: {e}")


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


@app.post("/tasks/{lang_str}")
def upload_and_run(
    lang_str: str, file: UploadFile = File(...), email: str | None = Form(None)
) -> dict:
    """
    upload a file to the server and run the task with specified language.
    It will return message, filename, file_path, file_size, job_id, language.
    """
    try:
        assert file.filename

        original_file_path = UPLOAD_DIR / file.filename
        with open(original_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(original_file_path)

        # Convert full language name to short code
        language_code_list = []
        for lang in lang_str.split("+"):
            language_code_list.append(Language.from_fullname(lang))

        # submit the task
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobInfo(
            future=executor.submit(
                run_translation_task, original_file_path, language_code_list, email
            ),
            filename=file.filename,  # pyright: ignore[reportArgumentType]
            file_size=file_size,
            language=lang_str,
            email=email,
        )

        return {
            "message": f"File '{file.filename}' uploaded and task started successfully with language: {lang_str}",
            "job_id": job_id,
            "filename": file.filename,
            "file_size": file_size,
            "language": lang_str,
            "email": email,
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
        "email": job_info.email,
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
                "email": job_info.email,
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
