from rest_framework import serializers

AUDIENCE_CHOICES = ["child", "adult", "elderly", "nonnative"]


class SimplifyRequestSerializer(serializers.Serializer):
    text = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=12000,  # keep prompts small enough for free-tier token limits
    )
    audience = serializers.ChoiceField(choices=AUDIENCE_CHOICES, default="adult")
    language = serializers.CharField(default="en", allow_blank=True, max_length=40)
