import uvicorn
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from app.api.v1.api_router import router as api_router
from app.core.firebase_config import firebase_config
import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE FIREBASE ---
# Usar Application Default Credentials para GCP
# En desarrollo local, esto usará las credenciales del archivo JSON
# En Cloud Run, esto usará las credenciales del servicio automáticamente

# Inicializar la app de Firebase. Solo se hace una vez.
try:
    firebase_admin.get_app()
    logger.info("✅ Firebase app ya inicializada")
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
    except Exception as e:
        logger.error(f"❌ Error inicializando Firebase: {e}")
        # Continuar sin Firebase si hay error

# Inicializar Firebase
try:
    firebase_config.initialize()
    logger.info("✅ Firebase config inicializada")
except Exception as e:
    logger.error(f"❌ Error inicializando Firebase config: {e}")

app = FastAPI(
    title="Barrio Fuerte - Motor de Análisis",
    version="0.1.0"
)

# Obtener una referencia a la base de datos de Firestore
try:
    db = firestore.client()
    logger.info("✅ Conexión con Firestore establecida.")
except Exception as e:
    logger.error(f"❌ Error conectando a Firestore: {e}")
    db = None

# --- FIN DE CONFIGURACIÓN ---

# Incluir el router de la API v1
try:
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ API router incluido")
except Exception as e:
    logger.error(f"❌ Error incluyendo API router: {e}")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint raíz para verificar que la API está viva."""
    return {"status": "API online", "message": "Barrio Fuerte Backend funcionando correctamente"}

@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint de health check más detallado."""
    health_status = {
        "status": "healthy",
        "firebase_initialized": firebase_config._initialized if hasattr(firebase_config, '_initialized') else False,
        "firestore_connected": db is not None
    }
    return health_status

@app.get("/test-firestore", tags=["Tests"])
def test_firestore_connection():
    """Endpoint para probar la escritura y lectura en Firestore."""
    if not db:
        raise HTTPException(status_code=500, detail="Firestore no está disponible")
    
    try:
        # Asegurar que Firebase esté inicializado
        firebase_config.initialize()
        db = firebase_config.firestore

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

