import uuid
from django.db import models

# Create your models here.

class TenderDocument(models.Model):
    class IngestionStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        INGESTED = 'ingested', 'Ingested'
        FAILED = 'failed', 'Failed'
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    tender_code = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='tender_docs/%Y/%m/%d/')
    
    # Metadata fields otomatis diekstrak saat ingestion
    original_filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=15, db_index=True)
    file_size_bytes = models.PositiveBigIntegerField()
    
    status = models.CharField(
        max_length=20,
        choices=IngestionStatus.choices,
        default=IngestionStatus.INGESTED,
        db_index=True
    )
    
    mock_extracted_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tender Document'
        verbose_name_plural = 'Tender Documents'
        
    def __str__(self):
        return f"[{self.tender_code}] {self.title} ({self.original_file_name})"