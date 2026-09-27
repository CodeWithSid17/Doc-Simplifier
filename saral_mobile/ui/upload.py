import asyncio
import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
    card,
    primary_button,
)


def show_upload(
    page,
    api,
    on_back,
    on_result,
):

    page.controls.clear()

    status = ft.Text(
        "PDF • JPG • PNG • TXT • DOCX • XLSX",
        color=TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    progress = ft.ProgressRing(
        visible=False,
    )

    file_picker = ft.FilePicker()

    async def upload_selected_file(file):

        progress.visible = True
        choose_button.disabled = True

        status.value = (
            f"Uploading {file.name}..."
        )

        page.update()

        try:

            if not file.path:

                status.value = (
                    "Unable to access the selected file."
                )

                return

            upload_status, upload_data = (
                await api.upload_document(
                    file_path=file.path,
                    file_name=file.name,
                )
            )

            print(
                "UPLOAD RESPONSE:",
                upload_status,
                upload_data,
            )

            if upload_status not in (200, 201):

                status.value = (
                    upload_data.get(
                        "error",
                        upload_data.get(
                            "detail",
                            "Upload failed.",
                        ),
                    )
                )

                return

            document = upload_data.get(
                "document"
            )

            if not document:

                status.value = (
                    "Server did not return a document."
                )

                return

            document_id = document.get(
                "id"
            )

            if not document_id:

                status.value = (
                    "Document ID missing."
                )

                return

            status.value = (
                "Reading document..."
            )

            page.update()

            extract_status, extract_data = (
                await api.extract_document(
                    document_id
                )
            )

            print(
                "EXTRACT RESPONSE:",
                extract_status,
                extract_data,
            )

            if extract_status not in (200, 201):

                status.value = (
                    extract_data.get(
                        "error",
                        extract_data.get(
                            "detail",
                            "Document extraction failed.",
                        ),
                    )
                )

                return

            status.value = (
                "Document ready."
            )

            page.update()

            on_result(
                extract_data
            )

        except Exception as exc:

            print(
                "UPLOAD ERROR:",
                repr(exc),
            )

            status.value = (
                f"Upload failed: {exc}"
            )

        finally:

            progress.visible = False
            choose_button.disabled = False

            page.update()

    async def choose_file():

        status.value = (
            "Choose a document..."
        )

        page.update()

        try:

            files = await file_picker.pick_files(
                dialog_title="Choose a document",
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[
                    "pdf",
                    "jpg",
                    "jpeg",
                    "png",
                    "txt",
                    "docx",
                    "xlsx",
                ],
            )

            print(
                "FILE PICKER RESULT:",
                files,
            )

            if not files:

                status.value = (
                    "No document selected."
                )

                page.update()

                return

            selected_file = files[0]

            status.value = (
                f"Selected: {selected_file.name}"
            )

            page.update()

            await upload_selected_file(
                selected_file
            )

        except Exception as exc:

            print(
                "FILE PICKER ERROR:",
                repr(exc),
            )

            status.value = (
                f"File picker error: {exc}"
            )

            page.update()

    choose_button = primary_button(
        "Choose document",
        lambda e: asyncio.create_task(
            choose_file()
        ),
        width=300,
    )

    # Flet 1.0 FilePicker is a service.
    page.services.append(
        file_picker
    )

    page.add(
        ft.Container(
            width=520,
            padding=24,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                tooltip="Back",
                                on_click=on_back,
                            ),

                            ft.Text(
                                "Upload document",
                                size=27,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                        ]
                    ),

                    ft.Text(
                        "Choose a document and Saral will make it easier to understand.",
                        color=TEXT_SECONDARY,
                    ),

                    card(
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.CLOUD_UPLOAD_OUTLINED,
                                        size=60,
                                        color=PRIMARY,
                                    ),
                                    width=100,
                                    height=100,
                                    bgcolor="#EFF6FF",
                                    border_radius=26,
                                    alignment=ft.Alignment.CENTER,
                                ),

                                ft.Text(
                                    "Upload a document",
                                    size=21,
                                    weight=ft.FontWeight.BOLD,
                                ),

                                ft.Text(
                                    "PDF • JPG • PNG • TXT • DOCX • XLSX",
                                    size=13,
                                    color=TEXT_SECONDARY,
                                ),

                                choose_button,

                                progress,

                                status,
                            ],
                            spacing=14,
                            horizontal_alignment=(
                                ft.CrossAxisAlignment.CENTER
                            ),
                        )
                    ),
                ],
                spacing=14,
            ),
        )
    )

    page.update()