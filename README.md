Vantedge Bid - Document Mock Ingestion API

Layanan backend REST API berbasis Python dan Django REST Framework (DRF) untuk simulasi ingestion (unggah dan ekstraksi) dokumen tender lelang. Proyek ini dikembangkan sebagai penyelesaian tugas Backend Engineer Vantedge Bid test.

Arsitektur dan Desain Kode (Clean Code)

Proyek ini mengimplementasikan pemisahan tanggung jawab (separation of concerns) agar View tetap tipis (thin views) dan logika bisnis mudah diuji. Lapisan kode dibagi ke dalam beberapa modul khusus di dalam app documents:

models.py: Skema database penyimpanan metadata dokumen tender dan indeks database.

serializers.py: Lapis validasi ketat untuk input (ekstensi file .pdf, .docx, .xlsx, dll., MIME type, dan pembatasan ukuran maksimal 5 MB).

services.py: Lapis logika bisnis untuk mock ingestion yang dibungkus dalam transaksi database atomik (@transaction.atomic).

selectors.py: Lapis abstraksi query database backend menggunakan agregasi Django ORM (Count, Sum, Avg) untuk menghasilkan metrik ringkasan secara efisien.

Prasyarat

Python 3.10+ (Diuji menggunakan Python 3.12)

Git

Cara Menjalankan Aplikasi Secara Lokal

1. Clone Repository

git clone https://github.com/ariodotpermadi/ventedge-bid-backend.git
cd ventedge-bid-backend


2. Siapkan Virtual Environment dan Dependensi

python3 -m venv venv
source venv/bin/activate  # Untuk Linux/macOS
# venv\Scripts\activate   # Untuk Windows

pip install -r requirements.txt


3. Migrasi Database
Aplikasi menggunakan SQLite sebagai database bawaan agar mudah dijalankan oleh reviewer tanpa konfigurasi environment eksternal tambahan.

python manage.py migrate


4. Jalankan Server

python manage.py runserver


Server akan berjalan di http://127.0.0.1:8000/.

Menjalankan Automated Tests

Proyek ini dilengkapi dengan serangkaian unit test untuk menguji validasi file dan fungsi query.

python manage.py test


Dokumentasi Endpoint API

1. Mock Document Ingestion

Mensimulasikan proses unggah dan indeks dokumen tender.

URL: /api/v1/documents/ingest/

Method: POST

Content-Type: multipart/form-data

Aturan Validasi:

Format file diizinkan: pdf, docx, doc, txt, xlsx, xls

Ukuran file maksimal: 5 MB

tender_code minimal 3 karakter.

Contoh Request (cURL):

curl -X POST http://127.0.0.1:8000/api/v1/documents/ingest/ \
  -F "tender_code=TND-2026-001" \
  -F "title=Dokumen Penawaran Teknis" \
  -F "file=@/lokasi/file/penawaran.pdf"


Contoh Response Sukses (201 Created):

{
  "message": "Dokumen tender berhasil di-ingest.",
  "data": {
    "id": "3cfa3f31-d60d-11f1-b8f2-5404a6a86e38",
    "tender_code": "TND-2026-001",
    "title": "Dokumen Penawaran Teknis",
    "original_filename": "penawaran.pdf",
    "file_extension": "pdf",
    "file_size_bytes": 77136,
    "file_size_kb": 75.33,
    "status": "ingested",
    "mock_extracted_summary": "[MOCK INGESTION] Dokumen 'penawaran.pdf' (75.33 KB) untuk lelang TND-2026-001 berhasil diindeks. Format terdeteksi: PDF.",
    "created_at": "2026-11-01T15:59:37.133908Z"
  }
}


2. Document Summary Query

Mengambil ringkasan data dokumen dan metrik agregasi backend.

URL: /api/v1/documents/summary/

Method: GET

Query Parameters (Opsional): ?tender_code=<KODE_TENDER> (untuk memfilter ringkasan berdasarkan kode tender spesifik).

Contoh Request (cURL):

curl -X GET "http://127.0.0.1:8000/api/v1/documents/summary/?tender_code=TND-2026-001"


Contoh Response Sukses (200 OK):

{
  "message": "Ringkasan dokumen berhasil diambil.",
  "data": {
    "filter_tender_code": "TND-2026-001",
    "overview": {
      "total_documents": 3,
      "total_size_bytes": 231408,
      "total_size_kb": 225.98,
      "average_size_kb": 75.33,
      "status_breakdown": {
        "ingested": 3,
        "failed": 0
      }
    },
    "breakdown_by_format": [
      {
        "file_extension": "pdf",
        "document_count": 3,
        "total_size_bytes": 231408
      }
    ],
    "recent_documents": [
      {
        "id": "3cfa3f31-d60d-11f1-b8f2-5404a6a86e38",
        "tender_code": "TND-2026-001",
        "title": "Dokumen Penawaran Teknis",
        "original_filename": "penawaran.pdf",
        "file_extension": "pdf",
        "file_size_bytes": 77136,
        "status": "ingested",
        "created_at": "2026-11-01T15:59:37.133908Z"
      }
    ]
  }
}
