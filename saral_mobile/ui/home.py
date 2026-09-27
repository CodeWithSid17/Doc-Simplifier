import asyncio
import flet as ft

from .theme import (
    PRIMARY,
    BACKGROUND,
    TEXT,
    TEXT_SECONDARY,
    SUCCESS,
    card,
    icon_box,
    pill,
    bottom_nav,
    section_title,
    page_shell,
)


def show_home(page, api, user, on_upload, on_simplify, on_documents, on_ai, on_profile):
    page.controls.clear()
    username = user.get("username") or "there"

    recent = ft.Column(spacing=10)
    loading = ft.ProgressRing(width=22, height=22, visible=True)

    async def load_recent():
        try:
            status, data = await api.get_documents()
            recent.controls.clear()

            if status == 401:
                recent.controls.append(ft.Text("Session expired. Please sign in again.", color="#DC2626"))
            elif status != 200:
                recent.controls.append(ft.Text("Couldn't load recent documents.", color="#DC2626"))
            elif not data:
                recent.controls.append(
                    card(
                        ft.Column(
                            [
                                icon_box(ft.Icons.DESCRIPTION_OUTLINED, size=54),
                                ft.Text("No documents yet", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text("Upload your first document to start.", color=TEXT_SECONDARY),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=22,
                    )
                )
            else:
                for doc in data[:3]:
                    recent.controls.append(
                        ft.Container(
                            bgcolor="#FFFFFF",
                            border=ft.Border.all(1, "#E7E7EE"),
                            border_radius=20,
                            padding=14,
                            content=ft.Row(
                                [
                                    icon_box(ft.Icons.DESCRIPTION_OUTLINED, size=46),
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
                                                        doc.get("status", "uploaded").capitalize(),
                                                        size=11,
                                                        color=SUCCESS if doc.get("status") == "completed" else TEXT_SECONDARY,
                                                    ),
                                                ],
                                                spacing=7,
                                            ),
                                        ],
                                        expand=True,
                                        spacing=5,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                                        tooltip="Ask AI",
                                        on_click=lambda e, d=doc: on_ai(d),
                                    ),
                                ],
                                spacing=12,
                            ),
                        )
                    )
        except Exception:
            recent.controls.clear()
            recent.controls.append(ft.Text("Unable to connect to Saral.", color="#DC2626"))
        finally:
            loading.visible = False
            page.update()

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Saral", size=30, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Text(f"Good to see you, {username} 👋", color=TEXT_SECONDARY),
                                ],
                                spacing=2,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.PERSON_OUTLINE,
                                tooltip="Profile",
                                on_click=on_profile,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),

                    ft.Container(
                        padding=24,
                        border_radius=28,
                        bgcolor=PRIMARY,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Text("Understand anything.", size=25, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                                ft.Text(
                                                    "Upload a document and let Saral turn complexity into clarity.",
                                                    color="#EDEBFF",
                                                    size=13,
                                                ),
                                            ],
                                            expand=True,
                                            spacing=7,
                                        ),
                                        ft.Icon(ft.Icons.AUTO_AWESOME, color="#FFFFFF", size=34),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Button(
                                    content="＋  Upload document",
                                    on_click=on_upload,
                                    width=220,
                                    height=48,
                                ),
                            ],
                            spacing=18,
                        ),
                    ),

                    section_title("AI tools"),

                    ft.Row(
                        [
                            ft.Container(
                                expand=True,
                                padding=16,
                                bgcolor="#FFFFFF",
                                border=ft.Border.all(1, "#E7E7EE"),
                                border_radius=20,
                                on_click=on_simplify,
                                content=ft.Column(
                                    [
                                        icon_box(ft.Icons.EDIT_DOCUMENT, size=44),
                                        ft.Text("Simplify", weight=ft.FontWeight.BOLD),
                                        ft.Text("Paste difficult text", size=11, color=TEXT_SECONDARY),
                                    ],
                                    spacing=7,
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                padding=16,
                                bgcolor="#FFFFFF",
                                border=ft.Border.all(1, "#E7E7EE"),
                                border_radius=20,
                                on_click=on_ai,
                                content=ft.Column(
                                    [
                                        icon_box(ft.Icons.CHAT_BUBBLE_OUTLINE, bgcolor="#F3F0FF", size=44),
                                        ft.Text("Ask AI", weight=ft.FontWeight.BOLD),
                                        ft.Text("Ask anything", size=11, color=TEXT_SECONDARY),
                                    ],
                                    spacing=7,
                                ),
                            ),
                        ],
                        spacing=12,
                    ),

                    section_title("Recent documents", "View all", on_documents),
                    loading,
                    recent,

                    bottom_nav(page, "Home", on_home=lambda e: None, on_documents=on_documents, on_ai=on_ai, on_profile=on_profile),
                ],
                spacing=14,
            )
        )
    )
    page.update()
    asyncio.create_task(load_recent())
