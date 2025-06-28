from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.services.storage_service import storage_service
from app.schemas.storage import ImageUploadRequest, ImageUploadResponse

router = APIRouter()

@router.get("/qr-image", tags=["Storage"])
def get_qr_image():
    """Endpoint para obtener la imagen QR.jpg desde Firebase Storage."""
    try:
        # Obtener la imagen desde el servicio
        image_data, content_type = storage_service.get_image("QR.jpg")
        
        # Retornar la imagen como respuesta para mostrar en frontend
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Content-Disposition": "inline; filename=QR.jpg",
                "Cache-Control": "public, max-age=3600"  # Cache por 1 hora
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="QR.jpg no encontrado en Firebase Storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la imagen QR: {str(e)}")

@router.get("/qr-image/download", tags=["Storage"])
def download_qr_image():
    """Endpoint para descargar la imagen QR.jpg desde Firebase Storage."""
    try:
        # Obtener la imagen desde el servicio
        image_data, content_type = storage_service.get_image("QR.jpg")
        
        # Retornar la imagen como respuesta para descargar
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=QR.jpg",
                "Cache-Control": "no-cache"  # No cache para descargas
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="QR.jpg no encontrado en Firebase Storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar la imagen QR: {str(e)}")

@router.get("/image/{filename}", tags=["Storage"])
def get_image(filename: str):
    """Endpoint genérico para obtener cualquier imagen desde Firebase Storage (para mostrar en frontend)."""
    try:
        # Obtener la imagen desde el servicio
        image_data, content_type = storage_service.get_image(filename)
        
        # Retornar la imagen como respuesta para mostrar en frontend
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"{filename} no encontrado en Firebase Storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la imagen {filename}: {str(e)}")

@router.get("/image/{filename}/download", tags=["Storage"])
def download_image(filename: str):
    """Endpoint genérico para descargar cualquier imagen desde Firebase Storage."""
    try:
        # Obtener la imagen desde el servicio
        image_data, content_type = storage_service.get_image(filename)
        
        # Retornar la imagen como respuesta para descargar
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache"  # No cache para descargas
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"{filename} no encontrado en Firebase Storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar la imagen {filename}: {str(e)}")

@router.post("/upload/payment", response_model=ImageUploadResponse, tags=["Storage"])
def upload_payment_image(request: ImageUploadRequest):
    """Endpoint para subir imágenes de pagos a la carpeta 'payments'."""
    try:
        # Subir la imagen usando el servicio (automáticamente a la carpeta 'payments')
        result = storage_service.upload_base64_image(
            base64_data=request.base64_data,
            folder="payments"
        )
        
        # Agregar el campo success
        result["success"] = True
        
        return ImageUploadResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error en el formato de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen de pago: {str(e)}") 