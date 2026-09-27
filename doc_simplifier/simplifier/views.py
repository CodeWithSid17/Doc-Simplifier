from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from .document_extractors import (
    DocumentExtractionError,
    extract_text,
)
from .models import Document, UserProfile
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    LoginSerializer,
    RegisterSerializer,
    SimplifyRequestSerializer,
)
from .services import (
    SimplifierError,
    simplify_document,
)


User = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):

    return Response(
        {
            "status": "ok",
            "service": "saral-api",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data

    if User.objects.filter(
        username=data["username"]
    ).exists():

        return Response(
            {
                "error": "Username already exists."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(
        email=data["email"]
    ).exists():

        return Response(
            {
                "error": "Email already exists."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )

        UserProfile.objects.create(
            user=user,
            auth_provider="email",
        )

        token = Token.objects.create(
            user=user
        )

    except IntegrityError:

        return Response(
            {
                "error": "Unable to create account."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Account created successfully.",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):

    serializer = LoginSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data[
        "email"
    ].lower().strip()

    password = serializer.validated_data[
        "password"
    ]

    try:

        user = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        return Response(
            {
                "error": "Invalid email or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    authenticated_user = authenticate(
        username=user.username,
        password=password,
    )

    if authenticated_user is None:

        return Response(
            {
                "error": "Invalid email or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(
        user=user
    )

    return Response(
        {
            "message": "Login successful.",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):

    Token.objects.filter(
        user=request.user
    ).delete()

    return Response(
        {
            "message": "Logged out successfully."
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):

    return Response(
        {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def simplify_view(request):

    serializer = SimplifyRequestSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data

    try:

        result = simplify_document(
            text=data["text"],
            audience=data["audience"],
            language=data["language"],
        )

    except SimplifierError as exc:

        return Response(
            {
                "error": str(exc)
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def document_upload_view(request):

    serializer = DocumentUploadSerializer(
        data=request.data,
        context={
            "request": request
        },
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    document = serializer.save()

    return Response(
        {
            "message": "Document uploaded successfully.",
            "document": DocumentSerializer(
                document
            ).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_list_view(request):

    documents = Document.objects.filter(
        user=request.user
    )

    return Response(
        DocumentSerializer(
            documents,
            many=True,
        ).data
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_detail_view(
    request,
    document_id,
):

    try:

        document = Document.objects.get(
            id=document_id,
            user=request.user,
        )

    except Document.DoesNotExist:

        return Response(
            {
                "error": "Document not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        DocumentSerializer(document).data
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def document_delete_view(
    request,
    document_id,
):

    try:

        document = Document.objects.get(
            id=document_id,
            user=request.user,
        )

    except Document.DoesNotExist:

        return Response(
            {
                "error": "Document not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    document.file.delete(
        save=False
    )

    document.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def document_extract_view(
    request,
    document_id,
):

    try:

        document = Document.objects.get(
            id=document_id,
            user=request.user,
        )

    except Document.DoesNotExist:

        return Response(
            {
                "error": "Document not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    document.status = "processing"

    document.error_message = ""

    document.save(
        update_fields=[
            "status",
            "error_message",
            "updated_at",
        ]
    )

    try:

        extracted_text = extract_text(
            document
        )

        document.extracted_text = (
            extracted_text
        )

        document.status = "completed"

        document.error_message = ""

        document.save(
            update_fields=[
                "extracted_text",
                "status",
                "error_message",
                "updated_at",
            ]
        )

    except DocumentExtractionError as exc:

        document.status = "failed"

        document.error_message = str(
            exc
        )

        document.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        return Response(
            {
                "error": str(exc),
                "status": "failed",
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return Response(
        {
            "message": "Document extracted successfully.",
            "document": DocumentSerializer(
                document
            ).data,
            "text_length": len(
                extracted_text
            ),
        }
    )