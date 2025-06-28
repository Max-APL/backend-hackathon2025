import os
from typing import Optional, Type
from google import genai
from google.genai import types
from pydantic import BaseModel

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de Gemini
        """
        # Usar la API key proporcionada o la variable de entorno
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Intentar usar la variable de entorno
            env_api_key = os.getenv('GEMINI_API_KEY')
            if env_api_key:
                self.client = genai.Client(api_key=env_api_key)
            else:
                raise ValueError("Se requiere una API key de Gemini")
    
    async def generate_object_with_schema(
        self,
        schema: Type[BaseModel],
        prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        root_prompt: str = ""
    ) -> BaseModel:
        """
        Genera un objeto estructurado usando Gemini con un schema específico
        
        Args:
            schema: Clase Pydantic que define la estructura de salida
            prompt: Prompt principal para el usuario
            model: Modelo de Gemini a usar
            temperature: Temperatura para la generación (0.0 - 2.0)
            root_prompt: Prompt del sistema (opcional)
        
        Returns:
            Instancia del schema con los datos generados
        """
        try:
            # Construir el prompt completo
            full_prompt = prompt
            if root_prompt:
                full_prompt = f"{root_prompt}\n\n{prompt}"
            
            # Configurar la generación con schema estructurado
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=temperature
            )
            
            # Generar contenido estructurado
            response = self.client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=config
            )
            
            # Usar el método parsed para obtener el objeto estructurado
            if hasattr(response, 'parsed') and response.parsed:
                if isinstance(response.parsed, schema):
                    return response.parsed
                else:
                    # Convertir dict a schema
                    parsed_dict = response.parsed if isinstance(response.parsed, dict) else {}
                    return schema(**parsed_dict)
            else:
                # Fallback: intentar parsear el texto JSON
                import json
                if response.text:
                    parsed_data = json.loads(response.text)
                    return schema(**parsed_data)
                else:
                    raise ValueError("No se recibió respuesta del modelo")
            
        except Exception as e:
            raise Exception(f"Error al generar objeto con schema: {str(e)}")
    
    def generate_content(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Genera contenido simple usando Gemini (sin schema)
        """
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text or ""
        except Exception as e:
            raise Exception(f"Error al generar contenido: {str(e)}") 