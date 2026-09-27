from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SimplifyRequestSerializer
from .services import simplify_document, SimplifierError


@api_view(["GET"])
def health_check(request):
    """Simple endpoint to confirm the API is alive (used by uptime pings)."""
    return Response({"status": "ok"})


@api_view(["POST"])
def simplify_view(request):
    serializer = SimplifyRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        result = simplify_document(
            text=data["text"],
            audience=data["audience"],
            language=data["language"],
        )
    except SimplifierError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(result, status=status.HTTP_200_OK)
