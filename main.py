import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import List


def run_task(cmd: str) -> str:
    """
    execute a single command. you can print the log you want here.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ▶️ Running: {cmd}")
    subprocess.run(cmd, shell=True)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Finished: {cmd}")
    return cmd


def main():
    # 1) task list
    tasks = [
        "python A.py",
        "python A.py",
        "python B.py",
        "python B.py",
    ]

    # 2) create a thread pool
    with ThreadPoolExecutor(max_workers=1) as executor:
        # submit() immediately put the task into the "invisible queue", and return a Future
        futures: List[Future] = [executor.submit(run_task, cmd) for cmd in tasks]

        # do something after each task is done
        for future in as_completed(futures):
            cmd_done = future.result()  # run_task returns the cmd
            print(f"--> Task done: {cmd_done}")


if __name__ == "__main__":
    main()
