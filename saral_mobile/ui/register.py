import asyncio
import flet as ft

from .theme import PRIMARY, TEXT, TEXT_SECONDARY, ERROR, card


def show_register(page, api, on_success, on_back):
    page.controls.clear()

    username = ft.TextField(label="Name", border_radius=16)
    email = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL, border_radius=16)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True, border_radius=16)
    error = ft.Text("", color=ERROR, visible=False)
    button = ft.Button(content="Create account", width=360, height=52)
    progress = ft.ProgressRing(visible=False, width=22, height=22)

    async def register():
        if not username.value or not email.value or not password.value:
            error.value = "Complete all fields."
            error.visible = True
            page.update()
            return

        error.visible = False
        button.disabled = True
        progress.visible = True
        page.update()

        try:
            status, data = await api.register(
                username.value.strip(),
                email.value.strip(),
                password.value,
            )
            if status == 201 and api.token:
                on_success(data)
                return
            error.value = data.get("error", "Unable to create account.")
            error.visible = True
        except Exception:
            error.value = "Unable to connect to Saral."
            error.visible = True
        finally:
            button.disabled = False
            progress.visible = False
            page.update()

    button.on_click = lambda e: asyncio.create_task(register())

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=20,
            content=ft.Container(
                width=500,
                content=ft.Column(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                        ft.Text("Create your account", size=29, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Your documents stay connected to your Saral account.", color=TEXT_SECONDARY),
                        card(
                            ft.Column(
                                [
                                    username,
                                    email,
                                    password,
                                    ft.Row([button, progress], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                                    error,
                                ],
                                spacing=13,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=24,
                        ),
                    ],
                    spacing=12,
                ),
            ),
        )
    )
    page.update()
