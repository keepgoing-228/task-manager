import gradio as gr
import requests



def handle_language_selection(selected):
    all_option = [
        "ALL",
        "Traditional Chinese",
        "Simplified Chinese",
        "Japanese",
        "Korean",
        # "Spanish",
        # "French",
        # "German",
    ]
    if "ALL" in selected and set(selected) != set(all_option):
        return all_option
    if "ALL" not in selected and set(selected) == (set(all_option) - {"ALL"}):
        return []
    return selected


def handle_upload(file_path, language):
    if "ALL" in language:
        language.remove("ALL")

    if not language:
        return ["Please select at least one language", gr.Tabs(selected=0)]

    results = []
    try:
        with open(file_path, "rb") as f:
            for lang in language:
                files = {"file": f}

                response = requests.post(f"http://localhost:3030/tasks/{lang}", files=files)
                response.raise_for_status()
                result_json = response.json()
                results.append(result_json["message"])

        return ["\n\n".join(results), gr.Tabs(selected=1)]
    except requests.exceptions.RequestException as e:
        return [f"Upload failed: {str(e)}", gr.Tabs(selected=0)]
    except Exception as e:
        return [f"Error occurred: {str(e)}", gr.Tabs(selected=0)]


def fetch_tasks():
    try:
        response = requests.get("http://localhost:3030/tasks/")
        response.raise_for_status()
        tasks = response.json()
        if tasks and "jobs" in tasks and tasks["jobs"]:
            jobs_info = []
            has_pending_jobs = False
            for job in tasks["jobs"]:
                if job["status"] != "done":
                    has_pending_jobs = True
                    job_info = f"Job ID: {job['job_id']}\n"
                    job_info += f"Status: {job['status']}\n"
                    job_info += f"File: {job['filename']}\n"
                    job_info += f"Language: {job['language']}\n"
                    job_info += "-" * 40 + "\n"
                    jobs_info.append(job_info)
            if has_pending_jobs:
                return "\n".join(jobs_info)
            else:
                return "All tasks are done"
        else:
            return "No tasks available"
    except Exception as e:
        return f"Error fetching tasks: {str(e)}"


with gr.Blocks(
    theme=gr.themes.Default(
        text_size=gr.themes.sizes.Size(
            name="text_lg",
            xxs="14px",
            xs="16px",
            sm="18px",
            md="20px",
            lg="24px",
            xl="28px",
            xxl="40px",
        )
    )
) as demo:
    # Top Title and Generate Button
    with gr.Row():
        with gr.Column(scale=3):
            html = """
                <div>
                    <h1 style="padding-left: 19px"> ASRtranslate</h1>
                    <p style="padding-left: 19px">powered by AI Lab</p>
                </div>
            """
            gr.HTML(html)
        with gr.Column(scale=1):
            upload_button = gr.Button(
                "Upload file", elem_id="upload-btn", scale=2, variant="primary"
            )

    # Tabs for Setting, Theme, and Result
    with gr.Tabs() as tabs:
        with gr.TabItem("Setting", id=0):
            gr.Markdown("### Select file:")
            with gr.Row():
                file_input = gr.UploadButton(
                    label="Upload file",
                    file_types=[".txt", ".pdf", ".docx", ".doc"],
                    file_count="single",
                    interactive=True,
                )
                # file_input = gr.Textbox(
                #     label="",
                #     value="/home/tim/Downloads/1.txt",
                #     placeholder="Enter your file address here, e.g. /home/tim/Downloads/1.txt",
                #     interactive=True,
                # )

            gr.Markdown("### Select language:")
            language_dropdown = gr.CheckboxGroup(
                choices=[
                    "ALL",
                    "Traditional Chinese",
                    "Simplified Chinese",
                    "Japanese",
                    "Korean",
                    # "Spanish",
                    # "French",
                    # "German",
                ],
                label="",
                value=["Traditional Chinese"],
                interactive=True,
            )

            gr.Markdown("### Email address:")
            email_input = gr.Textbox(label="", placeholder="Enter your email here")

        with gr.TabItem("Monitor", id=1):
            gr.Markdown("### Process:")
            process_textbox = gr.Textbox(
                label="", value="None is processing...", interactive=False
            )

            gr.Markdown("### Next:")
            next_textbox = gr.TextArea(
                label="",
                value="None will be next",
                interactive=False,
                lines=5,
            )

            # Add refresh button
            refresh_button = gr.Button("Refresh Tasks")

    # Logic to update preview and handle events
    language_dropdown.change(
        fn=handle_language_selection,
        inputs=[language_dropdown],
        outputs=[language_dropdown],
    )

    upload_button.click(
        fn=handle_upload,
        inputs=[file_input, language_dropdown],
        outputs=[process_textbox, tabs],
    ).then(
        fn=fetch_tasks,
        inputs=[],
        outputs=[next_textbox],
    )

    refresh_button.click(
        fn=fetch_tasks,
        inputs=[],
        outputs=[next_textbox],
    )

demo.launch(server_name="0.0.0.0")
