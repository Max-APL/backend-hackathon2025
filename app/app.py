import uvicorn
from fastapi import FastAPI, HTTPException
import logging
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear la app FastAPI primero
app = FastAPI(
    title="Barrio Fuerte - Motor de Análisis",
    version="0.1.0"
)

# Inicializar servicios de forma opcional
firebase_initialized = False
db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from app.core.firebase_config import firebase_config
    
    # Inicializar Firebase de forma opcional
    try:
        firebase_admin.get_app()
        logger.info("✅ Firebase app ya inicializada")
        firebase_initialized = True
    except ValueError:
        logger.info("🔄 Inicializando Firebase app...")
        try:
            # Si estamos en desarrollo local y existe el archivo de credenciales
            if os.path.exists("hackaton-a44c8-f3d9ad76a54d.json"):
                logger.info("📁 Usando credenciales locales")
                cred = credentials.Certificate("hackaton-a44c8-f3d9ad76a54d.json")
                firebase_admin.initialize_app(cred)
            else:
                # En Cloud Run, usar Application Default Credentials
                logger.info("☁️ Usando Application Default Credentials")
                firebase_admin.initialize_app()
            logger.info("✅ Firebase app inicializada exitosamente")
            firebase_initialized = True
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {e}")
            # Continuar sin Firebase si hay error

    # Inicializar Firebase config
    if firebase_initialized:
        try:
            firebase_config.initialize()
            logger.info("✅ Firebase config inicializada")
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase config: {e}")

    # Obtener una referencia a la base de datos de Firestore
    if firebase_initialized:
        try:
            db = firestore.client()
            logger.info("✅ Conexión con Firestore establecida.")
        except Exception as e:
            logger.error(f"❌ Error conectando a Firestore: {e}")
            db = None

except ImportError as e:
    logger.error(f"❌ Firebase Admin no disponible: {e}")

# Incluir el router de la API v1 de forma opcional
try:
    from app.api.v1.api_router import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ API router incluido")
except Exception as e:
    logger.error(f"❌ Error incluyendo API router: {e}")
    # Crear un router básico si falla
    from fastapi import APIRouter
    fallback_router = APIRouter()
    
    @fallback_router.get("/test")
    def test_endpoint():
        return {"message": "API funcionando en modo básico"}
    
    app.include_router(fallback_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint raíz para verificar que la API está viva."""
    return {
        "status": "API online", 
        "message": "Barrio Fuerte Backend funcionando correctamente",
        "firebase_available": firebase_initialized
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint de health check más detallado."""
    health_status = {
        "status": "healthy",
        "firebase_initialized": firebase_initialized,
        "firestore_connected": db is not None,
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }
    return health_status

@app.get("/test-firestore", tags=["Tests"])
def test_firestore_connection():
    """Endpoint para probar la escritura y lectura en Firestore."""
    if not firebase_initialized or not db:
        raise HTTPException(status_code=500, detail="Firestore no está disponible")
    
    try:
        doc_ref = db.collection("test_collection").document("test_doc")
        doc_ref.set({"message": "Hola desde FastAPI!"})
        doc = doc_ref.get()
        if doc.exists:
            return {"status": "Éxito", "data_read": doc.to_dict()}
        else:
            raise HTTPException(status_code=500, detail="No se pudo leer el documento después de escribirlo.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Firestore: {str(e)}")

@app.get("/test-webhook", tags=["Tests"])
def test_webhook():
    """Endpoint para probar el webhook."""
    try:
        import requests
        url = "https://maxpasten.app.n8n.cloud/webhook-test/f182d304-1d67-4798-bd58-24dc84caec48"
        response = requests.get(url)
        
        return {
            "status_code": response.status_code,
            "response_text": response.text,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al probar webhook: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

