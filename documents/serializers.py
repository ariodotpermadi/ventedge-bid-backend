import os
from email.mime import application

from rest_framework import serializers
from .models import TenderDocument

ALLOWED_FILE_EXTENSIONS = ['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls']
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel"
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

class DocumentIngestionSerializer(serializers.Serializer):
    tender_code = serializers.CharField(max_length=50, trim_whitespace=True)
    title = serializers.CharField(max_length=255, trim_whitespace=True)
    file = serializers.FileField(write_only=True)
    
    def validate_tender_code(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Kode tender minimal harus 3 karakter.")
        return value.upper() 
    
    def validate_file(self, uploaded_file):
        # validasi file kosong.
        if uploaded_file.size == 0:
            raise serializers.ValidationError("File tidak boleh kosong.")
        
        # validasi ukuran file
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
            current_mb = round(uploaded_file.size / (1024 * 1024), 2)
            raise serializers.ValidationError(f"Ukuran file ({current_mb} MB) melebihi batas maksimal {max_mb} MB.")
            
        # validasi ekstensi file
        _, ext = os.path.splitext(uploaded_file.name.lower())
        clean_ext = ext.lstrip('.')
        if clean_ext not in ALLOWED_FILE_EXTENSIONS:
            allowed_ext_str = ', '.join(ALLOWED_FILE_EXTENSIONS)
            raise serializers.ValidationError(f"Format file '{clean_ext}' tidak didukung. Gunakan format: {allowed_ext_str}.")
        
        # validasi mime / content-type
        content_type = getattr(uploaded_file, "content_type", None)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                f"Tipe konten '{content_type}' tidak valid untuk dokumen tender."
            )

        return uploaded_file
    
class TenderDocumentDetailSerializer(serializers.ModelSerializer):
    file_size_kb = serializers.SerializerMethodField()

    class Meta:
        model = TenderDocument
        fields = [
            "id",
            "tender_code",
            "title",
            "original_filename",
            "file_extension",
            "file_size_bytes",
            "file_size_kb",
            "status",
            "mock_extracted_summary",
            "created_at",
        ]

    def get_file_size_kb(self, obj) -> float:
        return round(obj.file_size_bytes / 1024, 2)