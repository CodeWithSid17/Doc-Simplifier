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


def show_simplify(
    page,
    api,
    on_back,
):

    page.controls.clear()

    text_input = ft.TextField(
        label="Paste difficult text here",
        multiline=True,
        min_lines=10,
        max_lines=16,
        border_radius=14,
    )

    result_area = ft.Column(
        spacing=12
    )

    async def simplify():

        text = (
            text_input.value or ""
        ).strip()

        if not text:

            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    "Please enter some text."
                )
            )

            page.snack_bar.open = True

            page.update()

            return

        button.disabled = True

        button.content = "Understanding..."

        page.update()

        try:

            status, data = (
                await api.simplify(
                    text=text
                )
            )

            if status == 200:

                result_area.controls.clear()

                summary = data.get(
                    "summary_line",
                    "",
                )

                simplified = data.get(
                    "simplified",
                    "",
                )

                if summary:

                    result_area.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text(
                                        "In simple words",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color=PRIMARY,
                                    ),
                                    ft.Text(
                                        summary,
                                        size=16,
                                    ),
                                ],
                                spacing=8,
                            )
                        )
                    )

                result_area.controls.append(
                    card(
                        ft.Column(
                            [
                                ft.Text(
                                    "Explanation",
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    simplified,
                                    size=16,
                                ),
                            ],
                            spacing=8,
                        )
                    )
                )

            else:

                result_area.controls.clear()

                result_area.controls.append(
                    ft.Text(
                        data.get(
                            "error",
                            "Unable to simplify text.",
                        ),
                        color="#DC2626",
                    )
                )

        except Exception:

            result_area.controls.clear()

            result_area.controls.append(
                ft.Text(
                    "Unable to connect to Saral.",
                    color="#DC2626",
                )
            )

        finally:

            button.disabled = False

            button.content = "Simplify"

            page.update()

    button = primary_button(
        "Simplify",
        lambda e: asyncio.create_task(
            simplify()
        ),
        width=300,
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
                                on_click=on_back,
                            ),

                            ft.Text(
                                "Paste text",
                                size=27,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                        ]
                    ),

                    ft.Text(
                        "Paste difficult information and Saral will explain it simply.",
                        color=TEXT_SECONDARY,
                    ),

                    card(
                        ft.Column(
                            [
                                text_input,
                                button,
                            ],
                            spacing=14,
                        )
                    ),

                    result_area,
                ],
                spacing=14,
            ),
        )
    )

    page.update()