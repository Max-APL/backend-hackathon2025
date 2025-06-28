from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Inversor(BaseModel):
    """Esquema para los datos del inversor."""
    nombreCompleto: str
    email: str
    telefono: str

class InteresInversion(BaseModel):
    """Esquema para los datos de interés de inversión."""
    pymeID: str
    pymeNombre: str
    inversor: Inversor
    montoInteresInvertir: str
    aceptaTerminos: bool
    fechaInteres: datetime

class InvestmentInterestRequest(BaseModel):
    """Esquema para la solicitud de interés de inversión."""
    interesInversion: InteresInversion

class InvestmentInterestResponse(BaseModel):
    """Esquema para la respuesta de interés de inversión."""
    success: bool
    document_id: str
    message: str
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "document_id": "inversor_20241201_143022_123",
                "message": "Interés de inversión registrado exitosamente",
                "created_at": "2024-12-01T14:30:22.123456Z"
            }
        } 