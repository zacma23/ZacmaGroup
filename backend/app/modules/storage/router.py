"""File Storage Module.

Provides secure upload endpoints for passports, supporting documents,
and payment proof screenshots with type and size validation.
"""

from fastapi import APIRouter, File, Form, UploadFile, status

from app.models import FileUploadResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
):
    """Upload a file (passport, supporting document, payment receipt)."""
    result = await FileService.save_upload(file, category)
    return result
