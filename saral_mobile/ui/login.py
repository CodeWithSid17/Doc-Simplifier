import asyncio
import flet as ft

from .theme import PRIMARY, TEXT, TEXT_SECONDARY, ERROR, card, icon_box, page_shell


def show_login(page, api, on_success, on_register):
    page.controls.clear()

    email = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL, border_radius=16)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True, border_radius=16)
    error = ft.Text("", color=ERROR, visible=False)
    button = ft.Button(content="Sign in", width=360, height=52)
    progress = ft.ProgressRing(visible=False, width=22, height=22)

    async def login():
        if not email.value or not password.value:
            error.value = "Enter your email and password."
            error.visible = True
            page.update()
            return

        error.visible = False
        button.disabled = True
        progress.visible = True
        page.update()

        try:
            status, data = await api.login(email.value.strip(), password.value)
            if status == 200 and api.token:
                on_success(data)
                return
            error.value = data.get("error", "Login failed.")
            error.visible = True
        except Exception as exc:
            error.value = f"Unable to connect to Saral: {exc}"
            error.visible = True
        finally:
            button.disabled = False
            progress.visible = False
            page.update()

    button.on_click = lambda e: asyncio.create_task(login())

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=20,
            content=ft.Container(
                width=500,
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text("S", size=32, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            width=72,
                            height=72,
                            bgcolor=PRIMARY,
                            border_radius=24,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text("Welcome to Saral", size=30, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Upload it. Understand it. Ask anything.", color=TEXT_SECONDARY),
                        card(
                            ft.Column(
                                [
                                    ft.Text("Sign in", size=20, weight=ft.FontWeight.BOLD),
                                    email,
                                    password,
                                    ft.Row([button, progress], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                                    error,
                                    ft.Divider(),
                                    ft.TextButton("Create a new account", on_click=on_register),
                                ],
                                spacing=13,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=24,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
            ),
        )
    )
    page.update()
