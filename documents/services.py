import os
from django.db import transaction
from .models import TenderDocument

@transaction.atomic
def ingest_tender_document(*, tender_code=str, title=str, uploaded_file) -> TenderDocument:
    """
    Fungsi untuk menyimpan dokumen tender ke database.
    """
    # Ekstrak metadata file
    _, ext = os.path.splitext(uploaded_file.name.lower())
    clean_ext = ext.lstrip('.')
    size_kb = round(uploaded_file.size / 1024, 2)
    
    mock_summary = (
        f"[MOCK INGESTION] Dokumen '{uploaded_file.name}' ({size_kb} KB) "
        f"untuk lelang {tender_code} berhasil diindeks. Format terdeteksi: {clean_ext.upper()}."
    )
    
    
    # Simpan dokumen tender ke database
    document = TenderDocument.objects.create(
        tender_code=tender_code,
        title=title,
        uploaded_file=uploaded_file,
        original_filename=uploaded_file.name,
        file_extension=clean_ext,
        file_size_bytes=uploaded_file.size,
        mock_extracted_summary=mock_summary,
        status=TenderDocument.IngestionStatus.INGESTED
    )
    
    return document