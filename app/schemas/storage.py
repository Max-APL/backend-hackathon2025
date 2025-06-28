from pydantic import BaseModel, Field

class ImageUploadRequest(BaseModel):
    """Esquema para la solicitud de subida de imagen de pago."""
    
    base64_data: str

class ImageUploadResponse(BaseModel):
    """Esquema para la respuesta de subida de imagen."""
    
    success: bool
    filename: str
    storage_path: str
    url: str
    size: int
    content_type: str
    uploaded_at: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "filename": "20241201_143022_123.jpg",
                "storage_path": "payments/20241201_143022_123.jpg",
                "url": "gs://hackaton-a44c8.firebasestorage.app/payments/20241201_143022_123.jpg",
                "size": 12345,
                "content_type": "image/jpeg",
                "uploaded_at": "2024-12-01T14:30:22.123456Z"
            }
        }
    } 