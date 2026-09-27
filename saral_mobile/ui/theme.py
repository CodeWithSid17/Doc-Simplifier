import flet as ft


PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"

BACKGROUND = "#F7F9FC"

TEXT = "#102A43"
TEXT_SECONDARY = "#627D98"

WHITE = "#FFFFFF"

BORDER = "#E2E8F0"

SUCCESS = "#16A34A"
ERROR = "#DC2626"


def card(content):

    return ft.Container(
        content=content,
        bgcolor=WHITE,
        border_radius=18,
        padding=18,
    )


def primary_button(
    text,
    on_click,
    width=300,
):

    return ft.Button(
        content=text,
        width=width,
        height=50,
        on_click=on_click,
    )