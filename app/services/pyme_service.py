import asyncio
from typing import List, Dict, Any, Optional
from app.models.pyme_analysis import PymeAnalysis, PymeStructuredAnalysis
from app.services.gemini_service import GeminiService

class PymeService:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_service = GeminiService(api_key=api_key)
    
    async def analyze_pyme_with_ai(self, pyme_data: PymeAnalysis) -> Dict[str, Any]:
        """
        Analiza una Pyme usando Gemini AI con respuesta estructurada
        """
        try:
            # Convertir PymeAnalysis a dict
            pyme_dict = pyme_data.dict()
            
            # Usar prompt personalizado si se proporciona, sino usar el default
            custom_prompt = pyme_data.prompt
            # Verificar si el prompt personalizado no está vacío y no es solo espacios en blanco
            has_custom_prompt = custom_prompt is not None and custom_prompt.strip() != ""
            
            if has_custom_prompt and custom_prompt is not None:
                prompt = self._build_custom_analysis_prompt(pyme_dict, custom_prompt)
            else:
                prompt = self._build_analysis_prompt(pyme_dict)
            
            # Prompt del sistema
            root_prompt = """
            Eres un analista experto en negocios y evaluación de empresas. 
            Proporciona análisis concisos y puntuaciones basadas en la relevancia del negocio.
            Sé constructivo, positivo y proporciona recomendaciones accionables.
            Usa emojis apropiadamente para hacer el feedback más amigable.
            Mantén el resumen del análisis entre 300-800 caracteres para que sea conciso pero completo.
            """
            
            # Generar análisis estructurado usando la nueva función
            structured_analysis = await self.gemini_service.generate_object_with_schema(
                schema=PymeStructuredAnalysis,
                prompt=prompt,
                model="gemini-2.5-flash",
                temperature=0.7,
                root_prompt=root_prompt
            )
            
            # Retornar resultado combinado
            return {
                "pyme_data": pyme_dict,
                "ai_analysis": {
                    "success": True,
                    "analysis": structured_analysis,
                    "model_used": "gemini-2.5-flash",
                    "message": "Análisis estructurado generado exitosamente",
                    "custom_prompt_used": has_custom_prompt
                }
            }
            
        except Exception as e:
            return {
                "pyme_data": pyme_dict if 'pyme_dict' in locals() else {},
                "ai_analysis": {
                    "success": False,
                    "analysis": None,
                    "model_used": "gemini-2.5-flash",
                    "message": f"Error al analizar Pyme con AI: {str(e)}",
                    "custom_prompt_used": has_custom_prompt if 'has_custom_prompt' in locals() else False
                }
            }
    
    def _build_custom_analysis_prompt(self, pyme_data: Dict[str, Any], custom_prompt: str) -> str:
        """
        Construye el prompt usando el prompt personalizado proporcionado por el usuario
        """
        prompt = f"""
        {custom_prompt}

        DATOS DEL NEGOCIO:
        {{
            "address": "{pyme_data.get('address', '')}",
            "description": "{pyme_data.get('description', '')}",
            "id": "{pyme_data.get('id', '')}",
            "phone": "{pyme_data.get('phone', '')}",
            "price": {pyme_data.get('price', 0)},
            "rating": {pyme_data.get('rating', 0.0)},
            "reviews": {pyme_data.get('reviews', 0)},
            "reviews_data": {pyme_data.get('reviews_data', [])},
            "title": "{pyme_data.get('title', '')}",
            "type": "{pyme_data.get('type', '')}",
            "website": "{pyme_data.get('website', '')}"
        }}

        IMPORTANTE: 
        - Responde ÚNICAMENTE con el JSON estructurado según el esquema proporcionado.
        - El resumen del análisis debe tener entre 300-800 caracteres.
        """
        
        return prompt
    
    def _build_analysis_prompt(self, pyme_data: Dict[str, Any]) -> str:
        """
        Construye el prompt para el análisis de Pyme con score de relevancia único
        """
        prompt = f"""
        Analiza el siguiente negocio y proporciona una evaluación de relevancia:

        DATOS DEL NEGOCIO:
        {{
            "address": "{pyme_data.get('address', '')}",
            "description": "{pyme_data.get('description', '')}",
            "id": "{pyme_data.get('id', '')}",
            "phone": "{pyme_data.get('phone', '')}",
            "price": {pyme_data.get('price', 0)},
            "rating": {pyme_data.get('rating', 0.0)},
            "reviews": {pyme_data.get('reviews', 0)},
            "reviews_data": {pyme_data.get('reviews_data', [])},
            "title": "{pyme_data.get('title', '')}",
            "type": "{pyme_data.get('type', '')}",
            "website": "{pyme_data.get('website', '')}"
        }}

        INSTRUCCIONES DE ANÁLISIS:

        Evalúa la **relevancia** del negocio en una escala del 0 al 100 basándote en:

        1. **Calificación y Reputación** (40% del score):
           - Calificación promedio y número de reseñas
           - Calidad del feedback de los clientes
           - Consistencia en la satisfacción del cliente

        2. **Presencia y Visibilidad** (30% del score):
           - Información de contacto completa
           - Sitio web funcional
           - Descripción clara y atractiva

        3. **Competitividad y Posicionamiento** (20% del score):
           - Precio competitivo para el tipo de negocio
           - Diferenciación en el mercado
           - Tipo de negocio y demanda

        4. **Potencial de Crecimiento** (10% del score):
           - Oportunidades de mejora identificadas
           - Capacidad de escalabilidad
           - Fortalezas del negocio

        **Cálculo del Score**:
        - Comienza con un puntaje base de **70 puntos**
        - Ajusta según los criterios anteriores
        - Asegúrate de que el puntaje final esté entre **0 y 100**

        **Resumen del Análisis**:
        - Proporciona un resumen completo y conciso (300-800 caracteres)
        - Incluye fortalezas principales del negocio
        - Identifica áreas de mejora específicas
        - Da recomendaciones accionables
        - Usa un tono positivo y constructivo
        - Incluye emojis apropiados
        - NO excedas los 800 caracteres

        **Formato de Respuesta**:
        - "relevance_score": puntuación de 0 a 100
        - "analysis_summary": resumen completo del análisis (máximo 800 caracteres)

        IMPORTANTE: Responde ÚNICAMENTE con el JSON estructurado según el esquema proporcionado.
        """
        
        return prompt