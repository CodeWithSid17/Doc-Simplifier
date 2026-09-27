import os

from rest_framework import serializers

from .models import Document


ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".jpg": "jpg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".txt": "txt",
    ".docx": "docx",
    ".xlsx": "xlsx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


class RegisterSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=150
    )

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate_email(self, value):
        return value.lower().strip()


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )


class SimplifyRequestSerializer(serializers.Serializer):

    text = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=12000,
    )

    audience = serializers.ChoiceField(
        choices=[
            "child",
            "adult",
            "elderly",
            "nonnative",
        ],
        default="adult",
    )

    language = serializers.CharField(
        default="en",
        allow_blank=True,
        max_length=40,
    )


class DocumentUploadSerializer(serializers.ModelSerializer):

    file = serializers.FileField(
        write_only=True
    )

    class Meta:
        model = Document

        fields = [
            "id",
            "file",
            "original_filename",
            "file_type",
            "file_size",
            "audience",
            "language",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "original_filename",
            "file_type",
            "file_size",
            "status",
            "created_at",
        ]

    def validate_file(self, uploaded_file):

        if not uploaded_file:
            raise serializers.ValidationError(
                "Please select a file."
            )

        if uploaded_file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Unsupported file type. "
                "Allowed: PDF, JPG, JPEG, PNG, TXT, DOCX, XLSX."
            )

        return uploaded_file

    def create(self, validated_data):

        uploaded_file = validated_data["file"]

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        return Document.objects.create(
            user=self.context["request"].user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_type=ALLOWED_EXTENSIONS[extension],
            file_size=uploaded_file.size,
            audience=validated_data.get(
                "audience",
                "adult",
            ),
            language=validated_data.get(
                "language",
                "en",
            ),
            status="uploaded",
        )


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document

        fields = [
            "id",
            "original_filename",
            "file_type",
            "file_size",
            "audience",
            "language",
            "status",
            "error_message",
            "created_at",
            "updated_at",
        ]