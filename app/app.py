import uvicorn
from fastapi import FastAPI, HTTPException, APIRouter
import logging
import os
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicialización
app = FastAPI(title="Barrio Fuerte - Motor de Análisis", version="0.1.0")
firebase_initialized = False
db = None

# Constantes
CREDENTIALS_FILE = "hackaton-a44c8-f3d9ad76a54d.json"
USE_LOCAL_CREDENTIALS = os.path.exists(CREDENTIALS_FILE)
STORAGE_BUCKET = "hackaton-a44c8.firebasestorage.app"


def init_firebase():
    global firebase_initialized, db
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Verificar si Firebase ya está inicializado
        try:
            firebase_admin.get_app()
            logger.info("✅ Firebase app ya inicializada")
            firebase_initialized = True
        except ValueError:
            logger.info("🔄 Inicializando Firebase app...")
            try:
                if USE_LOCAL_CREDENTIALS:
                    cred = credentials.Certificate(CREDENTIALS_FILE)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': STORAGE_BUCKET
                    })
                    logger.info("📁 Credenciales locales usadas")
                else:
                    # En Cloud Run, usar Application Default Credentials
                    firebase_admin.initialize_app({
                        'storageBucket': STORAGE_BUCKET
                    })
                    logger.info("☁️ Application Default Credentials usadas")
                firebase_initialized = True
            except Exception as e:
                logger.error(f"❌ Error inicializando Firebase: {e}")
                return

        # Solo inicializar firebase_config si Firebase está disponible
        if firebase_initialized:
            try:
                from app.core.firebase_config import firebase_config
                firebase_config.initialize()
                logger.info("✅ Firebase config inicializada")
            except Exception as e:
                logger.error(f"❌ Error en firebase_config: {e}")
                # Continuar sin firebase_config

        # Obtener cliente de Firestore
        if firebase_initialized:
            try:
                db = firestore.client()
                logger.info("✅ Conexión con Firestore establecida")
            except Exception as e:
                logger.error(f"❌ Error conectando a Firestore: {e}")
                db = None

    except ImportError as e:
        logger.error(f"❌ Firebase Admin no disponible: {e}")


def include_routers():
    try:
        from app.api.v1.api_router import api_router
        app.include_router(api_router, prefix="/api/v1")
        logger.info("✅ API router incluido")
    except Exception as e:
        logger.error(f"❌ Error incluyendo API router: {e}")
        fallback_router = APIRouter()

        @fallback_router.get("/test")
        def test_endpoint():
            return {"message": "API funcionando en modo básico"}

        app.include_router(fallback_router, prefix="/api/v1")


# Ejecutar inicializaciones
init_firebase()
include_routers()


@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "API online",
        "message": "Barrio Fuerte Backend funcionando correctamente",
        "firebase_available": firebase_initialized
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy",
        "firebase_initialized": firebase_initialized,
        "firestore_connected": db is not None,
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }


@app.get("/test-firestore", tags=["Tests"])
def test_firestore_connection():
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
