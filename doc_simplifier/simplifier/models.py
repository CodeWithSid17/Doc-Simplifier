from django.conf import settings
from django.db import models


class UserProfile(models.Model):

    AUTH_PROVIDER_CHOICES = [
        ("email", "Email"),
        ("google", "Google"),
        ("mobile", "Mobile"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    mobile_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_PROVIDER_CHOICES,
        default="email",
    )

    is_mobile_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.email or self.user.username


class Document(models.Model):

    STATUS_CHOICES = [
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("jpg", "JPG"),
        ("jpeg", "JPEG"),
        ("png", "PNG"),
        ("txt", "TXT"),
        ("docx", "DOCX"),
        ("xlsx", "XLSX"),
    ]

    AUDIENCE_CHOICES = [
        ("child", "Child"),
        ("adult", "Adult"),
        ("elderly", "Elderly"),
        ("nonnative", "Non-native English speaker"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    file = models.FileField(
        upload_to="documents/%Y/%m/%d/"
    )

    original_filename = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
    )

    file_size = models.PositiveBigIntegerField(
        default=0
    )

    extracted_text = models.TextField(
        blank=True,
        default="",
    )

    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="adult",
    )

    language = models.CharField(
        max_length=40,
        default="en",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="uploaded",
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_filename