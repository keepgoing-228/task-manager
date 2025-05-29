import queue
import subprocess
import threading
import time

# create the lock
task_lock = threading.Lock()


def worker(queue: queue.Queue, worker_id: int):
    while True:
        cmd = queue.get()
        if cmd is None:
            queue.task_done()
            break

        # get the lock, ensure the command is executed synchronously
        with task_lock:
            try:
                print(f"queue content: {queue.queue}")
                print(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')} Worker {worker_id} running command: {cmd}"
                )
                subprocess.run(cmd, shell=True)
                print(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')} Worker {worker_id} finished command: {cmd}"
                )
            except Exception as e:
                print(f"Worker {worker_id} error running command: {e}")

        queue.task_done()


def main():
    q = queue.Queue()

    # create two worker threads
    workers = []
    for i in range(2):
        t = threading.Thread(target=worker, args=(q, i + 1), daemon=True)
        workers.append(t)

    tasks = [
        "python A.py",
        "python A.py",
        "python B.py",
        "python B.py",
    ]

    # add the tasks to the queue
    for cmd in tasks:
        q.put(cmd)

    # start all worker threads
    for t in workers:
        t.start()

    # wait for all tasks to finish
    q.join()

    # tell the worker threads to stop (each thread one None)
    for _ in workers:
        q.put(None)

    # wait for all threads to finish
    for t in workers:
        t.join()


if __name__ == "__main__":
    main()
