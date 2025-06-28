from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from app.core.firebase_config import firebase_config
from app.schemas.investment import InteresInversion

class InvestmentService:
    """Servicio para operaciones de inversión."""
    
    def __init__(self):
        self.db = firebase_config.firestore
        self.collection_name = "inversor"
    
    def create_investment_interest(self, interes_inversion: InteresInversion) -> Dict[str, Any]:
        """
        Crea un nuevo registro de interés de inversión en Firestore.
        
        Args:
            interes_inversion: Datos del interés de inversión
            
        Returns:
            dict: Información del documento creado
                {
                    "document_id": "inversor_20241201_143022_123",
                    "success": True,
                    "message": "Interés de inversión registrado exitosamente",
                    "created_at": "2024-12-01T14:30:22.123456Z"
                }
                
        Raises:
            Exception: Para errores de Firestore
        """
        try:
            # Generar ID único para el documento
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            unique_id = str(uuid.uuid4())[:8]
            document_id = f"inversor_{timestamp}_{unique_id}"
            
            # Preparar los datos para Firestore
            investment_data = {
                "pymeID": interes_inversion.pymeID,
                "pymeNombre": interes_inversion.pymeNombre,
                "inversor": {
                    "nombreCompleto": interes_inversion.inversor.nombreCompleto,
                    "email": interes_inversion.inversor.email,
                    "telefono": interes_inversion.inversor.telefono
                },
                "montoInteresInvertir": interes_inversion.montoInteresInvertir,
                "aceptaTerminos": interes_inversion.aceptaTerminos,
                "fechaInteres": interes_inversion.fechaInteres,
                "created_at": datetime.now(),
                "document_id": document_id
            }
            
            # Crear el documento en Firestore
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc_ref.set(investment_data)
            
            # Verificar que se creó correctamente
            doc = doc_ref.get()
            if not doc.exists:
                raise Exception("No se pudo crear el documento en Firestore")
            
            return {
                "document_id": document_id,
                "success": True,
                "message": "Interés de inversión registrado exitosamente",
                "created_at": datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Error al crear el interés de inversión: {str(e)}")
    
    def get_investment_interest(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro de interés de inversión por ID.
        
        Args:
            document_id: ID del documento
            
        Returns:
            dict: Datos del interés de inversión o None si no existe
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            raise Exception(f"Error al obtener el interés de inversión: {str(e)}")
    
    def get_investments_by_pyme(self, pyme_id: str) -> list:
        """
        Obtiene todos los intereses de inversión para una PYME específica.
        
        Args:
            pyme_id: ID de la PYME
            
        Returns:
            list: Lista de intereses de inversión
        """
        try:
            investments = []
            docs = self.db.collection(self.collection_name).where("pymeID", "==", pyme_id).stream()
            
            for doc in docs:
                investment_data = doc.to_dict()
                investment_data["document_id"] = doc.id
                investments.append(investment_data)
            
            return investments
            
        except Exception as e:
            raise Exception(f"Error al obtener los intereses de inversión: {str(e)}")
    
    def get_investments_by_investor_email(self, email: str) -> list:
        """
        Obtiene todos los intereses de inversión de un inversor específico.
        
        Args:
            email: Email del inversor
            
        Returns:
            list: Lista de intereses de inversión
        """
        try:
            investments = []
            docs = self.db.collection(self.collection_name).where("inversor.email", "==", email).stream()
            
            for doc in docs:
                investment_data = doc.to_dict()
                investment_data["document_id"] = doc.id
                investments.append(investment_data)
            
            return investments
            
        except Exception as e:
            raise Exception(f"Error al obtener los intereses de inversión: {str(e)}")

# Instancia global del servicio
investment_service = InvestmentService() 