import os
import json
import requests
from typing import Optional, Type
from pydantic import BaseModel

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de Gemini usando la API REST
        """
        # Usar la API key proporcionada o la variable de entorno
        if api_key:
            self.api_key = api_key
        else:
            # Intentar usar la variable de entorno
            env_api_key = os.getenv('GEMINI_API_KEY')
            if env_api_key:
                self.api_key = env_api_key
            else:
                raise ValueError("Se requiere una API key de Gemini")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
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
            
            # Preparar la solicitud a la API
            url = f"{self.base_url}/{model}:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            # Crear el esquema JSON para la respuesta estructurada
            schema_fields = {}
            for field_name, field_info in schema.__annotations__.items():
                if hasattr(schema, '__fields__') and field_name in schema.__fields__:
                    field = schema.__fields__[field_name]
                    schema_fields[field_name] = {
                        "type": "string" if field.type_ == str else "integer" if field.type_ == int else "number",
                        "description": field.field_info.description if hasattr(field.field_info, 'description') else ""
                    }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"""Responde ÚNICAMENTE con un JSON válido que contenga los siguientes campos:
{json.dumps(schema_fields, indent=2)}

Prompt: {full_prompt}

Responde solo con el JSON, sin texto adicional."""
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }
            
            # Hacer la solicitud
            response = requests.post(
                url,
                headers=headers,
                json=data,
                params={"key": self.api_key}
            )
            
            if response.status_code != 200:
                raise Exception(f"Error en la API: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Extraer el texto de la respuesta
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Intentar parsear como JSON
                try:
                    # Limpiar el texto para extraer solo el JSON
                    text = text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                    
                    parsed_data = json.loads(text)
                    return schema(**parsed_data)
                except json.JSONDecodeError:
                    # Si no es JSON válido, crear un objeto con valores por defecto
                    return schema(
                        relevance_score=50,  # Valor por defecto
                        analysis_summary=text[:2000]  # Limitar a 2000 caracteres
                    )
            else:
                raise ValueError("No se recibió respuesta del modelo")
            
        except Exception as e:
            raise Exception(f"Error al generar objeto con schema: {str(e)}")
    
    def generate_content(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Genera contenido simple usando Gemini (sin schema)
        """
        try:
            url = f"{self.base_url}/{model}:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                params={"key": self.api_key}
            )
            
            if response.status_code != 200:
                raise Exception(f"Error en la API: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return ""
                
        except Exception as e:
            raise Exception(f"Error al generar contenido: {str(e)}") 