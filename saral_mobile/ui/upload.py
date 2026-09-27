import asyncio
import os
import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    ERROR,
    SUCCESS,
    card,
    icon_box,
    page_shell,
)


SUPPORTED = ["pdf", "jpg", "jpeg", "png", "txt", "docx", "xlsx"]


def show_upload(page, api, on_back, on_result):
    page.controls.clear()

    picker = ft.FilePicker()
    selected = {"file": None}

    file_name = ft.Text("No document selected", color=TEXT_SECONDARY, max_lines=1)
    file_meta = ft.Text("Choose PDF, image, text, Word or Excel", size=12, color=TEXT_SECONDARY)
    status = ft.Text("", color=TEXT_SECONDARY)
    progress = ft.ProgressRing(visible=False, width=24, height=24)
    choose_button = ft.Button(content="Choose document", width=260, height=52)
    upload_button = ft.Button(content="Upload & understand", width=260, height=52, disabled=True)

    def set_status(text, color=TEXT_SECONDARY):
        status.value = text
        status.color = color

    async def process_file(file):
        selected["file"] = file
        file_name.value = file.name
        ext = os.path.splitext(file.name)[1].replace(".", "").upper()
        size_mb = (file.size or 0) / (1024 * 1024)
        file_meta.value = f"{ext or 'FILE'}  •  {size_mb:.2f} MB"
        upload_button.disabled = False
        set_status("Ready to upload.")
        page.update()

    async def choose_file():
        choose_button.disabled = True
        set_status("Opening file picker...")
        page.update()
        try:
            files = await picker.pick_files(
                dialog_title="Choose a document",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=SUPPORTED,
            )
            if files:
                await process_file(files[0])
            else:
                set_status("No document selected.")
        except Exception as exc:
            set_status(f"File picker error: {exc}", ERROR)
        finally:
            choose_button.disabled = False
            page.update()

    async def upload():
        file = selected["file"]
        if not file or not file.path:
            set_status("Please choose a document first.", ERROR)
            page.update()
            return

        choose_button.disabled = True
        upload_button.disabled = True
        progress.visible = True
        set_status("Uploading document...")
        page.update()

        try:
            upload_status, upload_data = await api.upload_document(file.path, file.name)

            if upload_status == 401:
                set_status("Your session expired. Please sign in again.", ERROR)
                return

            if upload_status not in (200, 201):
                set_status(
                    api._message(
                        type("Response", (), {"status_code": upload_status})(),
                        upload_data,
                    ),
                    ERROR,
                )
                return

            document = upload_data.get("document") or {}
            document_id = document.get("id")

            if not document_id:
                set_status("The server did not return a document ID.", ERROR)
                return

            set_status("Reading your document...")
            page.update()

            extract_status, extract_data = await api.extract_document(document_id)

            if extract_status == 401:
                set_status("Your session expired. Please sign in again.", ERROR)
                return

            if extract_status not in (200, 201):
                set_status(
                    extract_data.get("error", "Document extraction failed."),
                    ERROR,
                )
                return

            set_status("Document understood successfully.", SUCCESS)
            page.update()
            await asyncio.sleep(0.25)
            on_result(extract_data)

        except Exception as exc:
            set_status(f"Unable to process this document: {exc}", ERROR)
        finally:
            progress.visible = False
            choose_button.disabled = False
            upload_button.disabled = selected["file"] is None
            page.update()

    choose_button.on_click = lambda e: asyncio.create_task(choose_file())
    upload_button.on_click = lambda e: asyncio.create_task(upload())

    page.services.clear()
    page.services.append(picker)

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Text("Upload", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ]
                    ),
                    ft.Text(
                        "Upload once. Saral will read it, simplify it and prepare it for AI.",
                        color=TEXT_SECONDARY,
                    ),

                    card(
                        ft.Column(
                            [
                                icon_box(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=68),
                                ft.Text("Drop your document into Saral", size=19, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "PDF  •  JPG  •  PNG  •  TXT  •  DOCX  •  XLSX",
                                    size=12,
                                    color=TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                choose_button,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12,
                        ),
                        padding=28,
                    ),

                    card(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        icon_box(ft.Icons.DESCRIPTION_OUTLINED, size=48),
                                        ft.Column(
                                            [file_name, file_meta],
                                            expand=True,
                                            spacing=3,
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                upload_button,
                                ft.Row([progress, status], spacing=10),
                            ],
                            spacing=12,
                        )
                    ),

                    ft.Text(
                        "Maximum file size: 10 MB",
                        size=11,
                        color=TEXT_SECONDARY,
                    ),
                ],
                spacing=14,
            )
        )
    )
    page.update()
