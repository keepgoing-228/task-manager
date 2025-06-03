# Task Manager

## why using threading instead of multiprocessing?

According to [Multiprocessing vs Treading Python](https://stackoverflow.com/questions/3044580/multiprocessing-vs-threading-python?utm_source=chatgpt.com), multiprocessing is more suitable for CPU-bound tasks, and threading is more suitable for [I/O-bound](https://realnewbie.com/coding/python/https-www-example-com-cpu-computation-vs-io-operations-best-practices-threads-processes/) tasks.

- Multiprocessing uses multiple independent processes, each with its own separate memory space, to fully utilize multiple cores of the CPU for true parallel execution, bypassing the GIL limit, and is suitable for CPU-bound tasks.
- Threading creates multiple threads within a single process, resource sharing, and smaller overhead, but still GIL limit, and is suitable for I/O-bound tasks.

## why using ThreadPoolExecutor

This project is mainly I/O-bound, like file upload and command execution. Also, [ThreadPoolExecutor](https://realnewbie.com/coding/python/threadpoolexecutor-complete-guide-python-concurrency/) handles the queueing and scheduling of tasks when max_workers is set to 1. The effect is the same as asyncio, however, the principle is different. Check the [two ways to get better I/O performance](https://realnewbie.com/coding/python/threadpoolexecutor-vs-asyncio-complete-guide-examples/)

- Less memory usage:
  ThreadPoolExecutor creates multiple threads within a single process, resource sharing, and smaller overhead for I/O-bound tasks.
- Less code:
  No need to handle the complexity of data serialization, cross-process communication, etc.
