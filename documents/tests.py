from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
# Create your tests here.

class DocumentIngestionTests(APITestCase):
    def setUp(self):
        self.ingest_url = reverse("document-ingest")
        self.summary_url = reverse("document-summary")

    def test_valid_pdf_ingestion(self):
        pdf_file = SimpleUploadedFile(
            "proposal_teknis.pdf",
            b"%PDF-1.4 dummy content for bid document",
            content_type="application/pdf",
        )
        payload = {
            "tender_code": "tnd-001",
            "title": "Proposal Teknis Pengadaan Server",
            "file": pdf_file,
        }
        response = self.client.post(self.ingest_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["tender_code"], "TND-001")
        self.assertEqual(response.data["data"]["file_extension"], "pdf")

    def test_reject_invalid_file_format(self):
        exe_file = SimpleUploadedFile(
            "malware.exe",
            b"binary content",
            content_type="application/x-msdownload",
        )
        payload = {
            "tender_code": "TND-001",
            "title": "File Tidak Valid",
            "file": exe_file,
        }
        response = self.client.post(self.ingest_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_document_summary_query(self):
        for i in range(2):
            f = SimpleUploadedFile(
                f"doc_{i}.pdf",
                b"dummy pdf content " * 50,
                content_type="application/pdf",
            )
            self.client.post(
                self.ingest_url,
                {"tender_code": "TND-999", "title": f"Doc {i}", "file": f},
                format="multipart",
            )

        response = self.client.get(f"{self.summary_url}?tender_code=TND-999")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["overview"]["total_documents"], 2)