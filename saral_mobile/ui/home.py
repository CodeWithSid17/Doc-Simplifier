import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    WHITE,
    card,
)


def show_home(
    page,
    user,
    on_upload,
    on_simplify,
    on_documents,
    on_logout,
):

    page.controls.clear()

    username = user.get(
        "username",
        "there",
    )

    page.add(
        ft.Container(
            width=520,
            padding=24,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        "Saral",
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                    ),
                                    ft.Text(
                                        f"Hi, {username} 👋",
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=2,
                            ),

                            ft.IconButton(
                                icon=ft.Icons.PERSON_OUTLINE,
                            ),
                        ],
                        alignment=(
                            ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ),

                    ft.Container(height=6),

                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Understand anything.",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=WHITE,
                                ),

                                ft.Text(
                                    "Turn complicated documents and text into simple explanations.",
                                    color="#DBEAFE",
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=PRIMARY,
                        border_radius=22,
                        padding=22,
                    ),

                    ft.Container(height=4),

                    ft.Text(
                        "What do you want to understand?",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Row(
                        [
                            ft.Container(
                                expand=True,
                                padding=18,
                                bgcolor=WHITE,
                                border_radius=18,
                                on_click=on_upload,
                                content=ft.Column(
                                    [
                                        ft.Icon(
                                            ft.Icons.UPLOAD_FILE,
                                            size=32,
                                            color=PRIMARY,
                                        ),
                                        ft.Text(
                                            "Upload",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "PDF, JPG, TXT, DOCX, XLSX",
                                            size=11,
                                            color=TEXT_SECONDARY,
                                        ),
                                    ],
                                    spacing=7,
                                ),
                            ),

                            ft.Container(
                                expand=True,
                                padding=18,
                                bgcolor=WHITE,
                                border_radius=18,
                                on_click=on_simplify,
                                content=ft.Column(
                                    [
                                        ft.Icon(
                                            ft.Icons.EDIT_DOCUMENT,
                                            size=32,
                                            color=PRIMARY,
                                        ),
                                        ft.Text(
                                            "Paste text",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Explain difficult text",
                                            size=11,
                                            color=TEXT_SECONDARY,
                                        ),
                                    ],
                                    spacing=7,
                                ),
                            ),
                        ],
                        spacing=12,
                    ),

                    ft.Container(height=4),

                    ft.Row(
                        [
                            ft.Text(
                                "My Documents",
                                size=19,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.TextButton(
                                "View all",
                                on_click=on_documents,
                            ),
                        ],
                        alignment=(
                            ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ),

                    card(
                        ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.DESCRIPTION_OUTLINED,
                                    size=32,
                                    color=PRIMARY,
                                ),
                                ft.Text(
                                    "Your simplified documents will appear here.",
                                    color=TEXT_SECONDARY,
                                ),
                            ],
                            horizontal_alignment=(
                                ft.CrossAxisAlignment.CENTER
                            ),
                        )
                    ),

                    ft.Container(height=20),

                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.HOME,
                                tooltip="Home",
                            ),

                            ft.IconButton(
                                icon=ft.Icons.DESCRIPTION_OUTLINED,
                                tooltip="Documents",
                                on_click=on_documents,
                            ),

                            ft.Container(
                                expand=True
                            ),

                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                tooltip="Logout",
                                on_click=on_logout,
                            ),
                        ]
                    ),
                ],
                spacing=14,
            ),
        )
    )

    page.update()