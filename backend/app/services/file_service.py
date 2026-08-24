"""Shared File Storage Service.

Handles secure file uploads (passports, supporting documents, payment proof screenshots)
with file type and size validation, organized into local disk storage with cloud-ready
interface abstractions.
"""

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileService:
    @staticmethod
    def _ensure_upload_dir(category: str = "general") -> Path:
        base_dir = Path(settings.storage_upload_dir) / category
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    @staticmethod
    async def save_upload(file: UploadFile, category: str = "general") -> dict:
        """Validate and save an uploaded file (supporting Local Disk or Google Cloud Storage)."""
        provider = getattr(settings, "storage_provider", "local").lower()
        if provider == "gcs":
            from app.services.gcs_file_service import GcsFileService
            return await GcsFileService.upload_file(file, category)

        filename = file.filename or "upload.bin"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not permitted. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        content = await file.read()
        size = len(content)

        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size ({size / 1024 / 1024:.2f} MB) exceeds maximum allowed 10 MB limit.",
            )

        upload_dir = FileService._ensure_upload_dir(category)
        file_id = f"{uuid.uuid4().hex[:12]}_{filename.replace(' ', '_')}"
        file_path = upload_dir / file_id

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "file_id": file_id,
            "file_name": filename,
            "file_url": f"/uploads/{category}/{file_id}",
            "content_type": file.content_type or "application/octet-stream",
            "size_bytes": size,
            "category": category,
            "storage_provider": "local",
        }
