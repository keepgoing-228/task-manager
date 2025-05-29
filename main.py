import queue
import subprocess
import threading
import time


def worker(queue: queue.Queue):
    while True:
        cmd = queue.get()
        if cmd is None:
            queue.task_done()
            break

        try:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Running command: {cmd}")
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(f"Error running command: {e}")
        finally:
            queue.task_done()


def main():
    q = queue.Queue()
    t = threading.Thread(target=worker, args=(q,), daemon=True)

    tasks = [
        "python A.py",
        "python B.py",
        "python A.py",
    ]
    for cmd in tasks:
        q.put(cmd)

    # start the worker
    t.start()

    # wait for the worker to finish
    q.join()

    # tell the worker to stop
    q.put(None)
    t.join()


if __name__ == "__main__":
    main()
