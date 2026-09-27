import flet as ft

from services.api import SaralAPI

from ui.documents import show_documents
from ui.home import show_home
from ui.login import show_login
from ui.register import show_register
from ui.simplify import show_simplify
from ui.upload import show_upload
from ui.theme import BACKGROUND


def main(page: ft.Page):

    page.title = "Saral"

    page.bgcolor = BACKGROUND

    page.padding = 0

    page.scroll = ft.ScrollMode.AUTO

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )

    api = SaralAPI()

    state = {
        "user": None,
    }

    # =========================================================
    # NAVIGATION
    # =========================================================

    def login_success(data):

        state["user"] = data["user"]

        show_home_screen()

    def register_success(data):

        state["user"] = data["user"]

        show_home_screen()

    def show_login_screen():

        show_login(
            page=page,
            api=api,
            on_success=login_success,
            on_register=lambda e:
                show_register_screen(),
        )

    def show_register_screen():

        show_register(
            page=page,
            api=api,
            on_success=register_success,
            on_back=lambda e:
                show_login_screen(),
        )

    def show_home_screen():

        show_home(
            page=page,
            user=state["user"],
            on_upload=lambda e:
                show_upload_screen(),
            on_simplify=lambda e:
                show_simplify_screen(),
            on_documents=lambda e:
                show_documents_screen(),
            on_logout=lambda e:
                logout(),
        )

    def show_upload_screen():

        show_upload(
            page=page,
            api=api,
            on_back=lambda e:
                show_home_screen(),
            on_result=lambda data:
                show_document_result(data),
        )

    def show_simplify_screen():

        show_simplify(
            page=page,
            api=api,
            on_back=lambda e:
                show_home_screen(),
        )

    def show_documents_screen():

        show_documents(
            page=page,
            api=api,
            on_back=lambda e:
                show_home_screen(),
        )

    def show_document_result(data):

        page.controls.clear()

        document = data.get(
            "document",
            {},
        )

        filename = document.get(
            "original_filename",
            "Document",
        )

        extracted_length = data.get(
            "text_length",
            0,
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
                                    on_click=lambda e:
                                        show_home_screen(),
                                ),

                                ft.Text(
                                    "Document ready",
                                    size=27,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),

                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                                        size=55,
                                        color="#16A34A",
                                    ),

                                    ft.Text(
                                        filename,
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                    ),

                                    ft.Text(
                                        f"{extracted_length:,} characters extracted.",
                                    ),

                                    ft.Text(
                                        "The document is ready for AI simplification.",
                                    ),
                                ],
                                horizontal_alignment=(
                                    ft.CrossAxisAlignment.CENTER
                                ),
                                spacing=10,
                            ),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=20,
                            padding=25,
                        ),
                    ],
                    spacing=16,
                ),
            )
        )

        page.update()

    async def logout():

        await api.logout()

        state["user"] = None

        show_login_screen()

    # =========================================================
    # START
    # =========================================================

    show_login_screen()


if __name__ == "__main__":
    ft.run(main)