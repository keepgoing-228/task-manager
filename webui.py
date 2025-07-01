import gradio as gr
import requests
import pandas as pd
from pathlib import Path


def handle_language_selection(selected):
    all_option = [
        "ALL",
        "Traditional Chinese",
        "Simplified Chinese",
        # "Japanese",
        # "Korean",
        # "Spanish",
        # "French",
        # "German",
    ]
    if "ALL" in selected and set(selected) != set(all_option):
        return all_option
    if "ALL" not in selected and set(selected) == (set(all_option) - {"ALL"}):
        return []
    return selected


def handle_file_selection(files):
    """Handle file selection and return file info for display"""
    if files is None or len(files) == 0:
        return "No file selected"

    file_info = []
    # single file -> in our case
    if isinstance(files, str):
        file_path = Path(files)
        file_info.append(f"File Name: {file_path.name}")
    # multiple files
    else:
        for file_path in files:
            path = Path(file_path)
            file_info.append(f"File Name: {path.name}")

    return "\n".join(file_info)


def handle_upload(file_path, language):
    if "ALL" in language:
        language.remove("ALL")

    if not language:
        return ["Please select at least one language", gr.Tabs(selected=0)]

    results = []
    try:
        lang_str = "_".join(language)

        with open(file_path, "rb") as f:
            files = {"file": f}

            response = requests.post(
                f"http://localhost:3030/tasks/{lang_str}", files=files
            )
            response.raise_for_status()
            result_json = response.json()
            results.append(result_json["message"])

        return ["\n\n".join(results), gr.Tabs(selected=1)]
    except requests.exceptions.RequestException as e:
        return [f"Upload failed: {str(e)}", gr.Tabs(selected=0)]
    except Exception as e:
        return [f"Error occurred: {str(e)}", gr.Tabs(selected=0)]


def fetch_tasks_as_dataframe():
    """Fetch tasks and return as structured data for dataframe display"""
    try:
        response = requests.get("http://localhost:3030/tasks/")
        response.raise_for_status()
        tasks = response.json()
        if tasks and "jobs" in tasks and tasks["jobs"]:
            pending_jobs = []
            for job in tasks["jobs"]:
                pending_jobs.append(
                    {
                        "Job ID": job["job_id"],
                        "Status": job["status"],
                        "File": job["filename"],
                        "Language": job["language"],
                    }
                )

            df = pd.DataFrame(pending_jobs)
            return df

        else:
            return pd.DataFrame(
                [
                    {
                        "Status": "No tasks available",
                        "Job ID": "",
                        "File": "",
                        "Language": "",
                    }
                ]
            )
    except Exception as e:
        return pd.DataFrame(
            [
                {
                    "Error": f"Error fetching tasks: {str(e)}",
                    "Job ID": "",
                    "File": "",
                    "Language": "",
                }
            ]
        )


with gr.Blocks(
    theme=gr.themes.Default(  # type: ignore
        text_size=gr.themes.sizes.Size(  # type: ignore
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
                selected_file_display = gr.Textbox(
                    label="",
                    value="No file selected",
                    interactive=False,
                )
                file_input = gr.UploadButton(
                    label="Upload file",
                    file_types=[".txt", ".idml"],
                    file_count="single",
                    interactive=True,
                )

            gr.Markdown("### Select language:")
            language_dropdown = gr.CheckboxGroup(
                choices=[
                    "ALL",
                    "Traditional Chinese",
                    "Simplified Chinese",
                    # "Japanese",
                    # "Korean",
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
            process_text = gr.Textbox(
                label="Process Status",
                value="Ready to process files...",
                interactive=False,
                visible=False,
            )
            gr.Markdown("### Task Table:")
            dataframe = gr.Dataframe(
                value=fetch_tasks_as_dataframe(),
                interactive=False,
                wrap=True,
            )

            refresh_button = gr.Button("Refresh Tasks")

    # Logic to update preview and handle events
    language_dropdown.change(
        fn=handle_language_selection,
        inputs=[language_dropdown],
        outputs=[language_dropdown],
    )

    # Handle file selection
    file_input.upload(
        fn=handle_file_selection,
        inputs=[file_input],
        outputs=[selected_file_display],
    )

    upload_button.click(
        fn=handle_upload,
        inputs=[file_input, language_dropdown],
        outputs=[process_text, tabs],
    ).then(
        fn=fetch_tasks_as_dataframe,
        inputs=[],
        outputs=[dataframe],
    )

    refresh_button.click(
        fn=fetch_tasks_as_dataframe,
        inputs=[],
        outputs=[dataframe],
    )

demo.launch(server_name="0.0.0.0")
