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


def show_login(
    page,
    api,
    on_success,
    on_register,
):

    page.controls.clear()

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

    async def login():

        error.visible = False

        if not email.value or not password.value:

            error.value = (
                "Please enter your email and password."
            )

            error.visible = True

            page.update()

            return

        button.disabled = True

        button.content = "Signing in..."

        page.update()

        try:

            status, data = await api.login(
                email.value.strip(),
                password.value,
            )

            if status == 200:

                on_success(data)

                return

            error.value = data.get(
                "error",
                "Login failed.",
            )

            error.visible = True

        except Exception:

            error.value = (
                "Unable to connect to Saral."
            )

            error.visible = True

        finally:

            button.disabled = False

            button.content = "Sign in"

            page.update()

    button = primary_button(
        "Sign in",
        lambda e: asyncio.create_task(
            login()
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
                        ft.Container(
                            content=ft.Text(
                                "S",
                                size=34,
                                weight=ft.FontWeight.BOLD,
                                color=WHITE,
                            ),
                            width=70,
                            height=70,
                            bgcolor=PRIMARY,
                            border_radius=20,
                            alignment=ft.Alignment.CENTER,
                        ),

                        ft.Text(
                            "Welcome to Saral",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT,
                        ),

                        ft.Text(
                            "Understand documents in simple language.",
                            color=TEXT_SECONDARY,
                        ),

                        ft.Container(height=8),

                        card(
                            ft.Column(
                                [
                                    ft.Text(
                                        "Sign in",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),

                                    email,
                                    password,

                                    error,

                                    button,

                                    ft.Divider(),

                                    ft.TextButton(
                                        "Create a new account",
                                        on_click=on_register,
                                    ),
                                ],
                                spacing=14,
                            )
                        ),
                    ],
                    spacing=12,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),
            ),
        )
    )

    page.update()