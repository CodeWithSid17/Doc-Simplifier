import flet as ft

PRIMARY = "#6C5CE7"
PRIMARY_DARK = "#5748D6"
ACCENT = "#8B7CF6"
BACKGROUND = "#F7F7FB"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F1EFFF"
TEXT = "#171717"
TEXT_SECONDARY = "#737373"
BORDER = "#E7E7EE"
SUCCESS = "#16A34A"
ERROR = "#DC2626"
WARNING = "#D97706"
WHITE = "#FFFFFF"


def card(content, padding=18, radius=22):
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=radius,
        padding=padding,
    )


def primary_button(text, on_click, width=None, height=52):
    return ft.Button(
        content=text,
        width=width,
        height=height,
        on_click=on_click,
    )


def pill(text, bgcolor=SURFACE_SOFT, color=PRIMARY):
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color=color),
        bgcolor=bgcolor,
        border_radius=999,
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
    )


def icon_box(icon, bgcolor=SURFACE_SOFT, color=PRIMARY, size=48):
    return ft.Container(
        content=ft.Icon(icon, color=color, size=24),
        width=size,
        height=size,
        bgcolor=bgcolor,
        border_radius=16,
        alignment=ft.Alignment.CENTER,
    )


def page_shell(content, max_width=560):
    return ft.Container(
        width=max_width,
        padding=ft.Padding.only(left=18, right=18, top=18, bottom=28),
        content=content,
    )


def bottom_nav(page, active, on_home, on_documents, on_ai, on_profile):
    items = [
        ("Home", ft.Icons.HOME_OUTLINED, ft.Icons.HOME, on_home),
        ("Docs", ft.Icons.DESCRIPTION_OUTLINED, ft.Icons.DESCRIPTION, on_documents),
        ("AI", ft.Icons.AUTO_AWESOME_OUTLINED, ft.Icons.AUTO_AWESOME, on_ai),
        ("Profile", ft.Icons.PERSON_OUTLINE, ft.Icons.PERSON, on_profile),
    ]

    controls = []
    for label, inactive, selected, callback in items:
        icon = selected if active == label else inactive
        color = PRIMARY if active == label else TEXT_SECONDARY
        controls.append(
            ft.Container(
                expand=True,
                padding=8,
                border_radius=16,
                on_click=callback,
                content=ft.Column(
                    [
                        ft.Icon(icon, size=21, color=color),
                        ft.Text(
                            label,
                            size=10,
                            weight=ft.FontWeight.BOLD if active == label else ft.FontWeight.NORMAL,
                            color=color,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                ),
            )
        )

    return ft.Container(
        margin=ft.Margin.only(top=8),
        padding=ft.Padding.symmetric(horizontal=8, vertical=7),
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=24,
        content=ft.Row(controls, spacing=2),
    )


def section_title(title, action_text=None, on_action=None):
    controls = [ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT)]
    if action_text:
        controls.append(ft.TextButton(action_text, on_click=on_action))
    return ft.Row(
        controls,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )
