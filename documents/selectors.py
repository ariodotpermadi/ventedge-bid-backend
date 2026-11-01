from typing import Optional, Dict, Any
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import Coalesce
from .models import TenderDocument


def get_documents_summary(*, tender_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Fungsi query backend untuk mengambil ringkasan agregat dan daftar dokumen terbaru.
    Dapat difilter berdasarkan tender_code jika diberikan.
    """
    
    queryset = TenderDocument.objects.all()
    
    if tender_code:
        queryset = queryset.filter(tender_code__iexact=tender_code.strip())
        
        # Agregasi metrik utama dalam satu query ke database
    metrics = queryset.aggregate(
        total_documents=Count("id"),
        total_size_bytes=Coalesce(Sum("file_size_bytes"), 0),
        average_size_bytes=Coalesce(Avg("file_size_bytes"), 0.0),
        ingested_count=Count("id", filter=Q(status=TenderDocument.IngestionStatus.INGESTED)),
        failed_count=Count("id", filter=Q(status=TenderDocument.IngestionStatus.FAILED)),
    )
    
    # Ringkasan jumlah & ukuran per format file
    breakdown_by_format = list(
        queryset.values("file_extension").annotate(
            document_count=Count("id"),
            total_size_bytes=Coalesce(Sum("file_size_bytes"), 0)
        )
        .order_by("-document_count")
    )
    
    # 5 document terakhir masuk
    recent_documents = list(
        queryset.values(
            "id",
            "tender_code",
            "title",
            "original_filename",
            "file_extension",
            "file_size_bytes",
            "status",
            "created_at",
        )[:5]
    )
    
    return {
        "filter_tender_code": tender_code.upper() if tender_code else "ALL",
        "overview": {
            "total_documents": metrics["total_documents"],
            "total_size_bytes": metrics["total_size_bytes"],
            "total_size_kb": round(metrics["total_size_bytes"] / 1024, 2),
            "average_size_kb": round(metrics["average_size_bytes"] / 1024, 2),
            "status_breakdown": {
                "ingested": metrics["ingested_count"],
                "failed": metrics["failed_count"],
            },
        },
        "breakdown_by_format": breakdown_by_format,
        "recent_documents": recent_documents,
    }
        