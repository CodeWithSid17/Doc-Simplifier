from django.urls import path

from . import ai_views, views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/me/", views.me_view, name="me"),
    path("simplify/", views.simplify_view, name="simplify"),
    path("documents/upload/", views.document_upload_view, name="document-upload"),
    path("documents/", views.document_list_view, name="document-list"),
    path("documents/<int:document_id>/", views.document_detail_view, name="document-detail"),
    path("documents/<int:document_id>/delete/", views.document_delete_view, name="document-delete"),
    path("documents/<int:document_id>/extract/", views.document_extract_view, name="document-extract"),
    path("ai/analyze/", ai_views.analyze_view, name="ai-analyze"),
    path("ai/chat/", ai_views.chat_view, name="ai-chat"),
    path("ai/translate/", ai_views.translate_view, name="ai-translate"),
    path("ai/compare/", ai_views.compare_view, name="ai-compare"),
    path("documents/<int:document_id>/content/", ai_views.document_content_view, name="document-content"),
]
