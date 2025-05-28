# Task Manager

## why using threading instead of multiprocessing?

[Multiprocessing vs Treading Python](https://stackoverflow.com/questions/3044580/multiprocessing-vs-threading-python?utm_source=chatgpt.com)

- Multiprocessing uses multiple independent processes, each with its own separate memory space, to fully utilize multiple cores of the CPU for true parallel execution, bypassing the GIL limit, and is suitable for CPU-bound tasks.
- Threading creates multiple threads within a single process, resource sharing, and smaller overhead, but still GIL limit, and is suitable for I/O-bound tasks.
