from fastapi import APIRouter, HTTPException
from app.services.pyme_service import PymeService
from app.models.pyme_analysis import PymeAnalysis

router = APIRouter(prefix="/pyme", tags=["Pyme Analysis"])

# API Key de Gemini (en producción debería estar en variables de entorno)
GEMINI_API_KEY = "AIzaSyAJUKCsrO9jvT8OsXquyIOxqEQvrmdi5_c"

@router.post("/analyze-ai")
async def analyze_pyme_with_ai(pyme_data: PymeAnalysis):
    """
    Analiza una Pyme usando Gemini AI con respuesta estructurada
    Retorna un análisis con score de relevancia y resumen completo
    """
    try:
        service = PymeService(api_key=GEMINI_API_KEY)
        return await service.analyze_pyme_with_ai(pyme_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 