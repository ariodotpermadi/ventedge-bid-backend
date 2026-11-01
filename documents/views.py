from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DocumentIngestionSerializer, TenderDocumentDetailSerializer
from .services import ingest_tender_document
from .selectors import get_documents_summary
# Create your views here.

class DocumentMockIngestionAPIView(APIView):
    """
    POST /api/v1/documents/ingest/
    Endpoint untuk simulasi unggah dokumen tender lelang beserta validasi payload.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = DocumentIngestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        document = ingest_tender_document(
            tender_code=serializer.validated_data["tender_code"],
            title=serializer.validated_data["title"],
            uploaded_file=serializer.validated_data["file"],
        )

        output_serializer = TenderDocumentDetailSerializer(document)
        return Response(
            {
                "message": "Dokumen tender berhasil di-ingest.",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
        
class DocumentSummaryAPIView(APIView):
    """
    GET /api/v1/documents/summary/?tender_code=TND-2026-01
    Endpoint untuk mengambil ringkasan agregat data dokumen yang telah diunggah.
    """
    def get(self, request, *args, **kwargs):
        tender_code = request.query_params.get("tender_code")
        summary_data = get_documents_summary(tender_code=tender_code)
        return Response(
            {
                "message": "Ringkasan dokumen berhasil diambil.",
                "data": summary_data,
            },
            status=status.HTTP_200_OK,
        )
