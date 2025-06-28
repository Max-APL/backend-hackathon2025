from fastapi import APIRouter, HTTPException
from app.services.investment_service import investment_service
from app.schemas.investment import InvestmentInterestRequest, InvestmentInterestResponse

router = APIRouter()

@router.post("/interest", response_model=InvestmentInterestResponse, tags=["Investment"])
def create_investment_interest(request: InvestmentInterestRequest):
    """Endpoint para crear un nuevo interés de inversión."""
    try:
        # Crear el interés de inversión usando el servicio
        result = investment_service.create_investment_interest(request.interesInversion)
        
        return InvestmentInterestResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el interés de inversión: {str(e)}")

@router.get("/interest/{document_id}", tags=["Investment"])
def get_investment_interest(document_id: str):
    """Endpoint para obtener un interés de inversión por ID."""
    try:
        result = investment_service.get_investment_interest(document_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Interés de inversión no encontrado")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el interés de inversión: {str(e)}")

@router.get("/interest/pyme/{pyme_id}", tags=["Investment"])
def get_investments_by_pyme(pyme_id: str):
    """Endpoint para obtener todos los intereses de inversión de una PYME."""
    try:
        investments = investment_service.get_investments_by_pyme(pyme_id)
        
        return {
            "success": True,
            "count": len(investments),
            "data": investments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los intereses de inversión: {str(e)}")

@router.get("/interest/investor/{email}", tags=["Investment"])
def get_investments_by_investor(email: str):
    """Endpoint para obtener todos los intereses de inversión de un inversor."""
    try:
        investments = investment_service.get_investments_by_investor_email(email)
        
        return {
            "success": True,
            "count": len(investments),
            "data": investments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los intereses de inversión: {str(e)}") 