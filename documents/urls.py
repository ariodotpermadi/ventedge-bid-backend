from django.urls import path
from .views import DocumentMockIngestionAPIView, DocumentSummaryAPIView

urlpatterns = [
    path("ingest/", DocumentMockIngestionAPIView.as_view(), name="document-ingest"),
    path("summary/", DocumentSummaryAPIView.as_view(), name="document-summary"),
]