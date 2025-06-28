from typing import Tuple
import base64
import uuid
from datetime import datetime
from app.core.firebase_config import firebase_config

class StorageService:
    """Servicio para operaciones de Firebase Storage."""
    
    def __init__(self):
        self.bucket = firebase_config.storage_bucket
    
    def get_image(self, filename: str) -> Tuple[bytes, str]:
        """
        Obtiene una imagen desde Firebase Storage.
        
        Args:
            filename: Nombre del archivo en Storage
            
        Returns:
            Tuple[bytes, str]: (contenido de la imagen, tipo de contenido)
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            Exception: Para otros errores
        """
        try:
            # Obtener el blob (archivo) desde Firebase Storage
            blob = self.bucket.blob(filename)
            
            # Verificar si el archivo existe
            if not blob.exists():
                raise FileNotFoundError(f"{filename} no encontrado en Firebase Storage")
            
            # Descargar el contenido del archivo
            image_data = blob.download_as_bytes()
            
            # Obtener el tipo de contenido (MIME type) del archivo
            content_type = blob.content_type or "image/jpeg"
            
            return image_data, content_type
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Error al obtener la imagen {filename}: {str(e)}")
    
    def upload_base64_image(self, base64_data: str, folder: str = "payments") -> dict:
        """
        Sube una imagen en formato base64 a Firebase Storage.
        
        Args:
            base64_data: Imagen en formato base64 (con o sin data URL)
            folder: Carpeta donde guardar la imagen (default: "payments")
            
        Returns:
            dict: Información del archivo subido
                {
                    "filename": "20241201_143022_123456.jpg",
                    "storage_path": "payments/20241201_143022_123456.jpg",
                    "url": "gs://bucket/folder/filename.jpg",
                    "size": 12345,
                    "content_type": "image/jpeg",
                    "uploaded_at": "2024-01-01T12:00:00Z"
                }
                
        Raises:
            ValueError: Si el base64 es inválido
            Exception: Para otros errores
        """
        try:
            # Limpiar el base64 si viene con data URL
            if base64_data.startswith('data:'):
                # Extraer el tipo de contenido y los datos
                header, base64_data = base64_data.split(',', 1)
                content_type = header.split(':')[1].split(';')[0]
            else:
                content_type = "image/jpeg"  # Default
            
            # Decodificar base64
            try:
                image_data = base64.b64decode(base64_data)
            except Exception:
                raise ValueError("Formato base64 inválido")
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Incluye milisegundos
            extension = self._get_extension_from_content_type(content_type)
            filename = f"{timestamp}{extension}"
            
            # Construir la ruta completa en el bucket
            storage_path = f"{folder}/{filename}"
            
            # Subir el archivo
            blob = self.bucket.blob(storage_path)
            blob.upload_from_string(
                image_data,
                content_type=content_type
            )
            
            # Retornar información del archivo
            return {
                "filename": filename,
                "storage_path": storage_path,
                "url": f"gs://{self.bucket.name}/{storage_path}",
                "size": len(image_data),
                "content_type": content_type,
                "uploaded_at": datetime.now().isoformat() + "Z"
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error al subir la imagen: {str(e)}")
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Obtiene la extensión de archivo basada en el tipo de contenido."""
        content_type_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg"
        }
        return content_type_map.get(content_type, ".jpg")
    
    def delete_image(self, filename: str) -> bool:
        """
        Elimina una imagen de Firebase Storage.
        
        Args:
            filename: Nombre del archivo en Storage
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            Exception: Para errores de eliminación
        """
        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            return True
            
        except Exception as e:
            raise Exception(f"Error al eliminar la imagen {filename}: {str(e)}")
    
    def image_exists(self, filename: str) -> bool:
        """
        Verifica si una imagen existe en Firebase Storage.
        
        Args:
            filename: Nombre del archivo en Storage
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            blob = self.bucket.blob(filename)
            return blob.exists()
        except Exception:
            return False

# Instancia global del servicio
storage_service = StorageService() 