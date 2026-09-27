import asyncio

import flet as ft

from services.api import SaralAPI

from ui.ai_chat import show_ai_chat
from ui.documents import show_documents
from ui.home import show_home
from ui.login import show_login
from ui.profile import show_profile
from ui.register import show_register
from ui.simplify import show_simplify
from ui.upload import show_upload
from ui.theme import BACKGROUND


def main(page: ft.Page):
    page.title = "Saral"
    page.bgcolor = BACKGROUND
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    api = SaralAPI()
    state = {"user": None}

    def set_user(data):
        state["user"] = data.get("user", data)

    def show_login_screen():
        show_login(
            page=page,
            api=api,
            on_success=lambda data: (set_user(data), show_home_screen()),
            on_register=lambda e: show_register_screen(),
        )

    def show_register_screen():
        show_register(
            page=page,
            api=api,
            on_success=lambda data: (set_user(data), show_home_screen()),
            on_back=lambda e: show_login_screen(),
        )

    def show_home_screen():
        show_home(
            page=page,
            api=api,
            user=state["user"] or {},
            on_upload=lambda e: show_upload_screen(),
            on_simplify=lambda e: show_simplify_screen(),
            on_documents=lambda e: show_documents_screen(),
            on_ai=lambda e: show_ai_screen(),
            on_profile=lambda e: show_profile_screen(),
        )

    def show_upload_screen():
        show_upload(
            page=page,
            api=api,
            on_back=lambda e: show_home_screen(),
            on_result=lambda data: show_document_result(data),
        )

    def show_simplify_screen():
        show_simplify(
            page=page,
            api=api,
            on_back=lambda e: show_home_screen(),
        )

    def show_documents_screen():
        show_documents(
            page=page,
            api=api,
            on_back=lambda e: show_home_screen(),
            on_ai=lambda document: show_ai_screen(document),
        )

    def show_ai_screen(document=None):
        show_ai_chat(
            page=page,
            api=api,
            document=document,
            on_back=lambda e: show_home_screen(),
            on_documents=lambda e: show_documents_screen(),
        )

    def show_profile_screen():
        async def logout():
            try:
                await api.logout()
            finally:
                state["user"] = None
                show_login_screen()

        show_profile(
            page=page,
            user=state["user"] or {},
            on_back=lambda e: show_home_screen(),
            on_logout=lambda e: asyncio.create_task(logout()),
        )

    def show_document_result(data):
        document = data.get("document", {})
        filename = document.get("original_filename", "Document")
        text_length = data.get("text_length", 0)

        page.controls.clear()

        summary = ft.Text(
            "Your document has been uploaded and its text is ready for AI.",
            size=15,
            color="#737373",
        )

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                padding=22,
                content=ft.Container(
                    width=560,
                    content=ft.Column(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: show_home_screen(),
                            ),
                            ft.Container(
                                padding=28,
                                bgcolor="#FFFFFF",
                                border_radius=28,
                                border=ft.Border.all(1, "#E7E7EE"),
                                content=ft.Column(
                                    [
                                        ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.CHECK_CIRCLE,
                                                color="#16A34A",
                                                size=58,
                                            ),
                                            alignment=ft.Alignment.CENTER,
                                        ),
                                        ft.Text(
                                            "Document ready",
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            filename,
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            f"{text_length:,} characters extracted",
                                            color="#737373",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        summary,
                                        ft.Row(
                                            [
                                                ft.Button(
                                                    content="Ask AI",
                                                    on_click=lambda e: show_ai_screen(document),
                                                ),
                                                ft.Button(
                                                    content="My Documents",
                                                    on_click=lambda e: show_documents_screen(),
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=14,
                                ),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ),
            )
        )
        page.update()

    show_login_screen()


if __name__ == "__main__":
    ft.run(main)
