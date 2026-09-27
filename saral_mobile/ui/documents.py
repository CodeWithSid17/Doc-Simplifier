import asyncio
import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    ERROR,
    SUCCESS,
    card,
    icon_box,
    pill,
    page_shell,
    bottom_nav,
)


def show_documents(page, api, on_back, on_ai):
    page.controls.clear()

    items = ft.Column(spacing=10)
    loading = ft.ProgressRing(width=24, height=24)

    async def delete_document(document_id, row):
        row.opacity = 0.45
        page.update()
        try:
            status, data = await api.delete_document(document_id)
            if status in (200, 204):
                if row in items.controls:
                    items.controls.remove(row)
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text(data.get("error", "Unable to delete document.")))
                page.snack_bar.open = True
        except Exception:
            page.snack_bar = ft.SnackBar(content=ft.Text("Unable to connect to Saral."))
            page.snack_bar.open = True
        page.update()

    async def load():
        try:
            status, data = await api.get_documents()
            items.controls.clear()

            if status == 401:
                items.controls.append(ft.Text("Session expired. Please sign in again.", color=ERROR))
            elif status != 200:
                items.controls.append(ft.Text("Couldn't load your documents.", color=ERROR))
            elif not data:
                items.controls.append(
                    card(
                        ft.Column(
                            [
                                icon_box(ft.Icons.DESCRIPTION_OUTLINED, size=58),
                                ft.Text("Your library is empty", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text("Upload your first document to get started.", color=TEXT_SECONDARY),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=7,
                        ),
                        padding=28,
                    )
                )
            else:
                for doc in data:
                    status_value = doc.get("status", "uploaded")
                    color = SUCCESS if status_value == "completed" else TEXT_SECONDARY
                    row = ft.Container(
                        bgcolor="#FFFFFF",
                        border=ft.Border.all(1, "#E7E7EE"),
                        border_radius=22,
                        padding=15,
                    )
                    delete = ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Delete",
                        on_click=lambda e, d=doc["id"], r=row: asyncio.create_task(delete_document(d, r)),
                    )
                    ask = ft.Button(
                        content="Ask AI",
                        on_click=lambda e, d=doc: on_ai(d),
                    )
                    row.content = ft.Column(
                        [
                            ft.Row(
                                [
                                    icon_box(ft.Icons.DESCRIPTION_OUTLINED, size=48),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                doc.get("original_filename", "Document"),
                                                weight=ft.FontWeight.BOLD,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Row(
                                                [
                                                    pill(doc.get("file_type", "file").upper()),
                                                    ft.Text(
                                                        status_value.capitalize(),
                                                        size=11,
                                                        color=color,
                                                    ),
                                                ],
                                                spacing=7,
                                            ),
                                        ],
                                        expand=True,
                                        spacing=5,
                                    ),
                                    delete,
                                ],
                                spacing=10,
                            ),
                            ft.Row(
                                [
                                    ask,
                                    ft.Text(
                                        f"{(doc.get('file_size', 0) / 1024):.0f} KB",
                                        size=11,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=11,
                    )
                    items.controls.append(row)
        except Exception:
            items.controls.clear()
            items.controls.append(ft.Text("Unable to connect to Saral.", color=ERROR))
        finally:
            loading.visible = False
            page.update()

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Text("Documents", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ]
                    ),
                    ft.Text("Everything you've uploaded, in one place.", color=TEXT_SECONDARY),
                    loading,
                    items,
                    bottom_nav(
                        page,
                        "Docs",
                        on_home=on_back,
                        on_documents=lambda e: None,
                        on_ai=lambda e: on_ai(None),
                        on_profile=lambda e: on_back(e),
                    ),
                ],
                spacing=14,
            )
        )
    )
    page.update()
    asyncio.create_task(load())
