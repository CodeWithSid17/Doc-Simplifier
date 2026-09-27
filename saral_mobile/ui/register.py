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


def show_register(
    page,
    api,
    on_success,
    on_back,
):

    page.controls.clear()

    username = ft.TextField(
        label="Username",
        border_radius=12,
    )

    email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_radius=12,
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border_radius=12,
    )

    error = ft.Text(
        color="#DC2626",
        visible=False,
    )

    async def register():

        error.visible = False

        if (
            not username.value
            or not email.value
            or not password.value
        ):

            error.value = (
                "Please complete all fields."
            )

            error.visible = True

            page.update()

            return

        button.disabled = True

        button.content = "Creating account..."

        page.update()

        try:

            status, data = (
                await api.register(
                    username.value.strip(),
                    email.value.strip(),
                    password.value,
                )
            )

            if status == 201:

                on_success(data)

                return

            error.value = data.get(
                "error",
                "Unable to create account.",
            )

            error.visible = True

        except Exception:

            error.value = (
                "Unable to connect to Saral."
            )

            error.visible = True

        finally:

            button.disabled = False

            button.content = "Create account"

            page.update()

    button = primary_button(
        "Create account",
        lambda e: asyncio.create_task(
            register()
        ),
        width=450,
    )

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=24,
            content=ft.Container(
                width=480,
                content=ft.Column(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=on_back,
                        ),

                        ft.Text(
                            "Create your Saral account",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT,
                        ),

                        ft.Text(
                            "Your documents and explanations stay connected to your account.",
                            color=TEXT_SECONDARY,
                        ),

                        card(
                            ft.Column(
                                [
                                    username,
                                    email,
                                    password,

                                    error,

                                    button,
                                ],
                                spacing=14,
                            )
                        ),
                    ],
                    spacing=12,
                ),
            ),
        )
    )

    page.update()   