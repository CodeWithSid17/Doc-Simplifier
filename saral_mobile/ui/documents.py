import asyncio

import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
)


def show_documents(
    page,
    api,
    on_back,
):

    page.controls.clear()

    document_list = ft.Column(
        spacing=10
    )

    loading = ft.ProgressRing()

    async def load():

        try:

            status, data = (
                await api.get_documents()
            )

            loading.visible = False

            document_list.controls.clear()

            if status != 200:

                document_list.controls.append(
                    ft.Text(
                        "Could not load documents.",
                        color="#DC2626",
                    )
                )

            elif not data:

                document_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.DESCRIPTION_OUTLINED,
                                    size=42,
                                    color=PRIMARY,
                                ),
                                ft.Text(
                                    "No documents yet.",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Upload your first document from the home screen.",
                                    color=TEXT_SECONDARY,
                                ),
                            ],
                            horizontal_alignment=(
                                ft.CrossAxisAlignment.CENTER
                            ),
                        ),
                        bgcolor=WHITE,
                        border_radius=18,
                        padding=24,
                    )
                )

            else:

                for document in data:

                    document_list.controls.append(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Icon(
                                            ft.Icons.DESCRIPTION_OUTLINED,
                                            color=PRIMARY,
                                        ),
                                        width=46,
                                        height=46,
                                        bgcolor="#EFF6FF",
                                        border_radius=13,
                                        alignment=ft.Alignment.CENTER,
                                    ),

                                    ft.Column(
                                        [
                                            ft.Text(
                                                document[
                                                    "original_filename"
                                                ],
                                                weight=ft.FontWeight.BOLD,
                                            ),

                                            ft.Text(
                                                document.get(
                                                    "status",
                                                    "uploaded",
                                                ).capitalize(),
                                                size=12,
                                                color=TEXT_SECONDARY,
                                            ),
                                        ],
                                        expand=True,
                                        spacing=3,
                                    ),
                                ],
                                spacing=12,
                            ),
                            bgcolor=WHITE,
                            border_radius=16,
                            padding=14,
                        )
                    )

        except Exception:

            loading.visible = False

            document_list.controls.append(
                ft.Text(
                    "Unable to connect to Saral.",
                    color="#DC2626",
                )
            )

        page.update()

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
                                on_click=on_back,
                            ),

                            ft.Text(
                                "My Documents",
                                size=27,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                        ]
                    ),

                    loading,

                    document_list,
                ],
                spacing=14,
            ),
        )
    )

    page.update()

    asyncio.create_task(
        load()
    )