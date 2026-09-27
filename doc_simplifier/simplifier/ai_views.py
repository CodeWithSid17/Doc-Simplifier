import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Document
from .services import (
    SimplifierError,
    analyze_document,
    answer_document_question,
    compare_documents,
    translate_text,
)


def _text(value, name, limit=30000):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{name} is required.")
    return value[:limit]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_view(request):
    try:
        text = _text(request.data.get("text"), "text")
        language = _text(request.data.get("language", "en"), "language", 40)
        result = analyze_document(text, language)
        return Response(result)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except SimplifierError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_view(request):
    try:
        document_id = request.data.get("document_id")
        question = _text(request.data.get("question"), "question", 4000)
        document = Document.objects.get(id=document_id, user=request.user)
        if not document.extracted_text:
            return Response(
                {"error": "This document has not been extracted yet."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        result = answer_document_question(document.extracted_text, question)
        return Response(result)
    except Document.DoesNotExist:
        return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except SimplifierError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def translate_view(request):
    try:
        text = _text(request.data.get("text"), "text", 20000)
        language = _text(request.data.get("language"), "language", 40)
        result = translate_text(text, language)
        return Response(result)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except SimplifierError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def compare_view(request):
    try:
        a_id = request.data.get("document_a_id")
        b_id = request.data.get("document_b_id")
        a = Document.objects.get(id=a_id, user=request.user)
        b = Document.objects.get(id=b_id, user=request.user)
        if not a.extracted_text or not b.extracted_text:
            return Response(
                {"error": "Both documents must be extracted before comparison."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        result = compare_documents(a.extracted_text, b.extracted_text)
        return Response(result)
    except Document.DoesNotExist:
        return Response({"error": "One or both documents were not found."}, status=status.HTTP_404_NOT_FOUND)
    except SimplifierError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_content_view(request, document_id):
    try:
        document = Document.objects.get(id=document_id, user=request.user)
    except Document.DoesNotExist:
        return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "id": document.id,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.status,
            "error_message": document.error_message,
            "extracted_text": document.extracted_text,
            "has_extracted_text": bool(document.extracted_text),
        }
    )
