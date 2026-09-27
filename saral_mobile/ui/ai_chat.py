import asyncio
import flet as ft

from .theme import (
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
    ERROR,
    WARNING,
    SUCCESS,
    card,
    icon_box,
    page_shell,
)


def show_ai_chat(page, api, document=None, on_back=None, on_documents=None):
    page.controls.clear()

    selected = document or {}
    document_id = selected.get("id")

    analysis = ft.Column(spacing=10)
    messages = ft.Column(spacing=10)
    question = ft.TextField(
        hint_text="Ask anything about your document...",
        multiline=True,
        min_lines=1,
        max_lines=4,
        border_radius=18,
    )
    send = ft.Button(content="Ask", width=90, height=50)
    busy = ft.ProgressRing(visible=False, width=22, height=22)
    analysis_busy = ft.ProgressRing(width=22, height=22)

    def add_message(text, mine=False):
        messages.controls.append(
            ft.Container(
                alignment=ft.Alignment.CENTER_RIGHT if mine else ft.Alignment.CENTER_LEFT,
                content=ft.Container(
                    width=500,
                    padding=14,
                    border_radius=18,
                    bgcolor="#EEEAFE" if mine else "#FFFFFF",
                    border=ft.Border.all(1, "#E7E7EE"),
                    content=ft.Text(text, size=14),
                ),
            )
        )

    async def load_analysis():
        if not selected.get("extracted_text"):
            status, detail = await api.get_document(document_id) if document_id else (0, {})
            if status == 200:
                selected.update(detail)

        text = selected.get("extracted_text")
        if not text:
            analysis_busy.visible = False
            analysis.controls.append(ft.Text("This document has no extracted text yet.", color=ERROR))
            page.update()
            return

        try:
            status, data = await api.analyze(text)
            analysis.controls.clear()
            if status == 200:
                analysis.controls.append(
                    card(
                        ft.Column(
                            [
                                ft.Text("Quick understanding", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY),
                                ft.Text(data.get("summary", "No summary returned."), size=14),
                            ],
                            spacing=7,
                        )
                    )
                )
                if data.get("key_points"):
                    analysis.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("Key points", size=15, weight=ft.FontWeight.BOLD),
                                    *[ft.Text(f"• {x}") for x in data["key_points"]],
                                ],
                                spacing=5,
                            )
                        )
                    )
                if data.get("important_dates"):
                    analysis.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("Important dates", size=15, weight=ft.FontWeight.BOLD),
                                    *[ft.Text(f"• {x}") for x in data["important_dates"]],
                                ],
                                spacing=5,
                            )
                        )
                    )
                if data.get("actions"):
                    analysis.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("Action items", size=15, weight=ft.FontWeight.BOLD, color=SUCCESS),
                                    *[ft.Text(f"• {x}") for x in data["actions"]],
                                ],
                                spacing=5,
                            )
                        )
                    )
                if data.get("warnings"):
                    analysis.controls.append(
                        card(
                            ft.Column(
                                [
                                    ft.Text("Pay attention", size=15, weight=ft.FontWeight.BOLD, color=WARNING),
                                    *[ft.Text(f"• {x}") for x in data["warnings"]],
                                ],
                                spacing=5,
                            )
                        )
                    )
            else:
                analysis.controls.append(ft.Text(data.get("error", "AI analysis failed."), color=ERROR))
        except Exception:
            analysis.controls.append(ft.Text("Unable to load AI analysis.", color=ERROR))
        finally:
            analysis_busy.visible = False
            page.update()

    async def ask():
        value = (question.value or "").strip()
        if not value:
            return
        if not document_id:
            page.snack_bar = ft.SnackBar(content=ft.Text("Open Ask AI from a document first."))
            page.snack_bar.open = True
            page.update()
            return

        add_message(value, mine=True)
        question.value = ""
        send.disabled = True
        busy.visible = True
        page.update()

        try:
            status, data = await api.ask_document(document_id, value)
            if status == 200:
                answer = data.get("answer", "I couldn't generate an answer.")
                evidence = data.get("evidence") or []
                if evidence:
                    answer += "\n\n" + "\n".join(f"• {item}" for item in evidence)
                add_message(answer)
            else:
                add_message(data.get("error", "Unable to answer that question."))
        except Exception:
            add_message("Unable to connect to Saral.")
        finally:
            send.disabled = False
            busy.visible = False
            page.update()

    send.on_click = lambda e: asyncio.create_task(ask())

    quick_actions = [
        ("Summary", "Give me a short summary of this document."),
        ("Key points", "What are the most important points?"),
        ("Risks", "What should I be careful about?"),
        ("Actions", "What do I need to do and by when?"),
    ]

    quick_buttons = [
        ft.TextButton(label, on_click=lambda e, q=q: (setattr(question, "value", q), page.update()))
        for label, q in quick_actions
    ]

    page.add(
        page_shell(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_back),
                            ft.Column(
                                [
                                    ft.Text("Ask Saral", size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Text(
                                        selected.get("original_filename", "Document AI"),
                                        size=11,
                                        color=TEXT_SECONDARY,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                expand=True,
                                spacing=1,
                            ),
                        ]
                    ),

                    card(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        icon_box(ft.Icons.AUTO_AWESOME, size=46),
                                        ft.Column(
                                            [
                                                ft.Text("Your document, understood.", weight=ft.FontWeight.BOLD),
                                                ft.Text("Summary, risks, actions and dates at a glance.", size=12, color=TEXT_SECONDARY),
                                            ],
                                            expand=True,
                                            spacing=3,
                                        ),
                                        analysis_busy,
                                    ],
                                    spacing=10,
                                ),
                                ft.Row(quick_buttons, scroll=ft.ScrollMode.AUTO, spacing=2),
                            ],
                            spacing=10,
                        )
                    ),

                    analysis,
                    messages,
                    ft.Row([question, send, busy], vertical_alignment=ft.CrossAxisAlignment.END, spacing=7),
                ],
                spacing=12,
            )
        )
    )
    page.update()
    if document_id:
        asyncio.create_task(load_analysis())
