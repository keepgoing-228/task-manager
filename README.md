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

## Features

- File upload and translation task management
- Real-time task status monitoring
- **Email notification system** - Get notified when translation is complete
- Web UI for easy interaction
- RESTful API for programmatic access

## how to run the project

```bash
# Run the FastAPI server
./launch_fastapi.sh

# Run the Gradio web UI (in another terminal)
uv run python webui.py
```

## Email Notification Setup

The system now supports automatic email notifications when translation is complete. See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed setup instructions.

### Quick Setup

1. Set environment variable:
   ```bash
   export EMAIL_PASSWORD=your_email_password
   ```

2. Update email settings in `main.py`:
   ```python
   EMAIL_SERVER = "your_server_ip"
   EMAIL_PORT = 3030
   EMAIL_SENDER = "your_email@gmail.com"
   ```

3. Use the web UI or API with email parameter to receive notifications.

## API Usage

### Upload and translate with email notification

```bash
curl -X POST \
  -F "file=@your_file.idml" \
  -F "email=user@example.com" \
  http://localhost:3030/tasks/Simplified+Chinese
```

### Check task status

```bash
curl http://localhost:3030/tasks/status/{job_id}
```

### List all tasks

```bash
curl http://localhost:3030/tasks/
```

## Email Config

```json
{
	"sender": "",
	"password": "",
	"smtp_server": "mail.asrock.com.tw",
	"domain": "",
	"smtp_port": 587,
	"use_ntlm": true,
	"include_timestamp":true
}
```