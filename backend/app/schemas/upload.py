from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.models.data.upload import UploadStatus


class UploadCreate(BaseModel):
    accommodation_id: int
    filename: str


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upload_id: int
    accommodation_id: int
    org_id: int

    status: UploadStatus
    error_message: str | None
    file_path: str

    created_at: datetime
    updated_at: datetime


class UploadCreateResponse(UploadResponse):
    presigned_url: str
