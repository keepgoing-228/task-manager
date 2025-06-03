# Task Manager

## why using threading instead of multiprocessing?

[Multiprocessing vs Treading Python](https://stackoverflow.com/questions/3044580/multiprocessing-vs-threading-python?utm_source=chatgpt.com)

- Multiprocessing uses multiple independent processes, each with its own separate memory space, to fully utilize multiple cores of the CPU for true parallel execution, bypassing the GIL limit, and is suitable for CPU-bound tasks.
- Threading creates multiple threads within a single process, resource sharing, and smaller overhead, but still GIL limit, and is suitable for I/O-bound tasks.

## why using ThreadPoolExecutor

This project is mainly I/O-bound, like file upload and command execution. Also, ThreadPoolExecutor handles the queueing and scheduling of tasks when max_workers is set to 1, so we don't need to do that.

- Less memory usage:
  ThreadPoolExecutor creates multiple threads within a single process, resource sharing, and smaller overhead for I/O-bound tasks.
- Less code:
  No need to handle the complexity of data serialization, cross-process communication, etc.
