import flet as ft

from .theme import TEXT, TEXT_SECONDARY, ERROR, card, icon_box, page_shell, bottom_nav


def show_profile(page, user, on_back, on_logout):
    page.controls.clear()

    username = user.get("username", "Saral user")
    email = user.get("email", "")

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Text("Profile", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ]
                    ),
                    card(
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(username[:1].upper(), size=25, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    width=62,
                                    height=62,
                                    bgcolor="#6C5CE7",
                                    border_radius=22,
                                    alignment=ft.Alignment.CENTER,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(username, size=18, weight=ft.FontWeight.BOLD),
                                        ft.Text(email, size=12, color=TEXT_SECONDARY),
                                    ],
                                    expand=True,
                                    spacing=3,
                                ),
                            ],
                            spacing=14,
                        )
                    ),
                    card(
                        ft.Column(
                            [
                                ft.Text("Account", size=16, weight=ft.FontWeight.BOLD),
                                ft.ListTile(
                                    leading=icon_box(ft.Icons.SECURITY_OUTLINED, size=42),
                                    title=ft.Text("Security"),
                                    subtitle=ft.Text("Your account uses secure token authentication."),
                                ),
                                ft.ListTile(
                                    leading=icon_box(ft.Icons.LANGUAGE, size=42),
                                    title=ft.Text("Languages"),
                                    subtitle=ft.Text("English, Hindi and Marathi AI support."),
                                ),
                            ],
                            spacing=6,
                        )
                    ),
                    ft.Button(content="Sign out", on_click=on_logout, width=220, height=50),
                    bottom_nav(
                        page,
                        "Profile",
                        on_home=on_back,
                        on_documents=on_back,
                        on_ai=on_back,
                        on_profile=lambda e: None,
                    ),
                ],
                spacing=14,
            )
        )
    )
    page.update()
