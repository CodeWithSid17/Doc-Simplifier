"""
Saral - Document Simplifier mobile app (Flet 1.0)

Two screens in one page: Input (paste text, pick audience + language) and
Result (simplified text, warnings, actions). Calls the Django backend's
/api/simplify/ endpoint using httpx (async, non-blocking).

BEFORE RUNNING: set API_BASE_URL below.
- Testing on Android emulator, Django running on your PC:  http://10.0.2.2:8000
- Testing on a real phone, same Wi-Fi as your PC:            http://<your-pc-lan-ip>:8000
  (run Django with: python manage.py runserver 0.0.0.0:8000)
- Once deployed to Render:                                   https://your-app.onrender.com
"""
import asyncio
import httpx
import flet as ft

API_BASE_URL = "http://127.0.0.1:8000"  # <-- CHANGE THIS

AUDIENCE_OPTIONS = [
    ("child", "Child"),
    ("adult", "Adult"),
    ("elderly", "Elderly"),
    ("nonnative", "Non-native English speaker"),
]

LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("Hindi", "Hindi"),
    ("Marathi", "Marathi"),
    ("Tamil", "Tamil"),
    ("Spanish", "Spanish"),
]


def main(page: ft.Page):
    page.title = "Saral - Document Simplifier"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.WHITE

    # ---------- shared state ----------
    state = {"loading": False}

    # ---------- INPUT SCREEN CONTROLS ----------
    doc_input = ft.TextField(
        label="Paste your document text here",
        multiline=True,
        min_lines=8,
        max_lines=14,
        border_radius=12,
        text_size=16,
    )

    audience_dropdown = ft.Dropdown(
        label="Explain it for",
        value="adult",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in AUDIENCE_OPTIONS],
        border_radius=12,
    )

    language_dropdown = ft.Dropdown(
        label="Output language",
        value="en",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in LANGUAGE_OPTIONS],
        border_radius=12,
    )

    error_text = ft.Text(color=ft.Colors.RED_600, visible=False)

    progress_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    simplify_button = ft.Button(
        content=ft.Row(
            [progress_ring, ft.Text("Simplify", size=16)],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding.symmetric(vertical=18, horizontal=20),
        ),
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
    )

    input_view = ft.Column(
        [
            ft.Text("Saral", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Text(
                "Paste any confusing document and get it explained simply.",
                size=14,
                color=ft.Colors.GREY_700,
            ),
            ft.Container(height=10),
            doc_input,
            ft.Row([audience_dropdown, language_dropdown], spacing=12),
            error_text,
            ft.Container(height=6),
            simplify_button,
        ],
        spacing=14,
    )

    # ---------- RESULT SCREEN CONTAINER (filled dynamically) ----------
    result_view = ft.Column(spacing=16, visible=False)

    # ---------- helpers ----------
    def set_loading(is_loading: bool):
        state["loading"] = is_loading
        progress_ring.visible = is_loading
        simplify_button.disabled = is_loading

    def show_error(message: str):
        error_text.value = message
        error_text.visible = True

    def clear_error():
        error_text.visible = False
        error_text.value = ""

    def build_result_view(data: dict):
        result_view.controls.clear()

        result_view.controls.append(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_back_to_input),
                    ft.Text("Result", size=24, weight=ft.FontWeight.BOLD),
                ]
            )
        )

        # Summary line - the headline takeaway
        if data.get("summary_line"):
            result_view.controls.append(
                ft.Container(
                    content=ft.Text(
                        data["summary_line"],
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.BLUE_900,
                    ),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=16,
                    border_radius=12,
                )
            )

        # Simplified explanation
        result_view.controls.append(
            ft.Container(
                content=ft.Text(data.get("simplified", ""), size=16, color=ft.Colors.BLACK_87),
                bgcolor=ft.Colors.GREY_100,
                padding=16,
                border_radius=12,
            )
        )

        # Warnings
        warnings = data.get("warnings") or []
        if warnings:
            result_view.controls.append(
                ft.Text("Warnings", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
            )
            for w in warnings:
                result_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [ft.Text("\u26a0\ufe0f"), ft.Text(w, size=15, expand=True)],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.RED_50,
                        padding=12,
                        border_radius=10,
                    )
                )

        # Actions
        actions = data.get("actions") or []
        if actions:
            result_view.controls.append(
                ft.Text("Actions to take", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
            )
            for a in actions:
                result_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [ft.Text("\u2705"), ft.Text(a, size=15, expand=True)],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=12,
                        border_radius=10,
                    )
                )

        input_view.visible = False
        result_view.visible = True

    def go_back_to_input(e=None):
        result_view.visible = False
        input_view.visible = True

    # ---------- main action ----------
    async def on_simplify_click(e):
        clear_error()

        text = (doc_input.value or "").strip()
        if not text:
            show_error("Please paste some text first.")
            return

        set_loading(True)

        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/simplify/",
                    json={
                        "text": text,
                        "audience": audience_dropdown.value,
                        "language": language_dropdown.value,
                    },
                )

            if response.status_code == 200:
                build_result_view(response.json())
            else:
                try:
                    err_data = response.json()
                    msg = err_data.get("error") or str(err_data)
                except Exception:
                    msg = f"Server error ({response.status_code})"
                show_error(msg)

        except httpx.ConnectError:
            show_error("Could not connect to the server. Check API_BASE_URL and your network.")
        except httpx.TimeoutException:
            show_error("The request took too long. Please try again.")
        except Exception as exc:
            show_error(f"Unexpected error: {exc}")
        finally:
            set_loading(False)

    simplify_button.on_click = on_simplify_click

    page.add(input_view, result_view)


if __name__ == "__main__":
    ft.run(main)