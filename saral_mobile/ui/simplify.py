import asyncio
import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    ERROR,
    card,
    page_shell,
)


def show_simplify(page, api, on_back):
    page.controls.clear()

    text_input = ft.TextField(
        hint_text="Paste a clause, paragraph, policy or any difficult text...",
        multiline=True,
        min_lines=10,
        max_lines=18,
        border_radius=18,
        border_color="#E7E7EE",
        focused_border_color=PRIMARY,
    )
    audience = ft.Dropdown(
        label="Explain for",
        value="adult",
        options=[
            ft.DropdownOption(key="adult", text="Everyday adult"),
            ft.DropdownOption(key="child", text="10-year-old"),
            ft.DropdownOption(key="elderly", text="Older reader"),
            ft.DropdownOption(key="nonnative", text="Simple English"),
        ],
    )
    language = ft.Dropdown(
        label="Language",
        value="en",
        options=[
            ft.DropdownOption(key="en", text="English"),
            ft.DropdownOption(key="Hindi", text="Hindi"),
            ft.DropdownOption(key="Marathi", text="Marathi"),
        ],
    )
    result = ft.Column(spacing=12)
    button = ft.Button(content="Simplify with AI", width=240, height=52)
    progress = ft.ProgressRing(visible=False)

    async def run():
        text = (text_input.value or "").strip()
        if not text:
            page.snack_bar = ft.SnackBar(content=ft.Text("Paste some text first."))
            page.snack_bar.open = True
            page.update()
            return

        button.disabled = True
        progress.visible = True
        result.controls.clear()
        page.update()

        try:
            status, data = await api.simplify(
                text=text,
                audience=audience.value or "adult",
                language=language.value or "en",
            )
            if status == 200:
                result.controls.extend(
                    [
                        card(
                            ft.Column(
                                [
                                    ft.Text("In one sentence", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                                    ft.Text(data.get("summary_line", "No summary returned."), size=16),
                                ],
                                spacing=7,
                            )
                        ),
                        card(
                            ft.Column(
                                [
                                    ft.Text("Simple explanation", size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(data.get("simplified", "No explanation returned."), size=15),
                                ],
                                spacing=7,
                            )
                        ),
                    ]
                )
                if data.get("warnings"):
                    result.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("Pay attention", size=15, weight=ft.FontWeight.BOLD, color="#D97706"),
                                    *[ft.Text(f"• {x}") for x in data["warnings"]],
                                ],
                                spacing=6,
                            )
                        )
                    )
                if data.get("actions"):
                    result.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("What you need to do", size=15, weight=ft.FontWeight.BOLD, color=PRIMARY),
                                    *[ft.Text(f"• {x}") for x in data["actions"]],
                                ],
                                spacing=6,
                            )
                        )
                    )
            else:
                result.controls.append(ft.Text(data.get("error", "Unable to simplify text."), color=ERROR))
        except Exception:
            result.controls.append(ft.Text("Unable to connect to Saral.", color=ERROR))
        finally:
            button.disabled = False
            progress.visible = False
            page.update()

    button.on_click = lambda e: asyncio.create_task(run())

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Text("Simplify", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ]
                    ),
                    ft.Text("Turn complicated language into something you can act on.", color=TEXT_SECONDARY),
                    card(ft.Column([text_input, ft.Row([audience, language], spacing=10), button, progress], spacing=12)),
                    result,
                ],
                spacing=14,
            )
        )
    )
    page.update()
