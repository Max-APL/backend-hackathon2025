import uvicorn
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from app.api.v1.api_router import router as api_router
from app.core.firebase_config import firebase_config
import requests
from app.api.v1.api_router import router as api_router
import os

# --- CONFIGURACIÓN DE FIREBASE ---
# Usar Application Default Credentials para GCP
# En desarrollo local, esto usará las credenciales del archivo JSON
# En Cloud Run, esto usará las credenciales del servicio automáticamente

# Inicializar la app de Firebase. Solo se hace una vez.
try:
    firebase_admin.get_app()
except ValueError:
    # Si estamos en desarrollo local y existe el archivo de credenciales
    if os.path.exists("hackaton-a44c8-f3d9ad76a54d.json"):
        cred = credentials.Certificate("hackaton-a44c8-f3d9ad76a54d.json")
        firebase_admin.initialize_app(cred)
    else:
        # En Cloud Run, usar Application Default Credentials
        firebase_admin.initialize_app()

# Inicializar Firebase
firebase_config.initialize()

app = FastAPI(
    title="Barrio Fuerte - Motor de Análisis",
    version="0.1.0"
)

# Obtener una referencia a la base de datos de Firestore
db = firestore.client()
print("✅ Conexión con Firestore establecida.")
# --- FIN DE CONFIGURACIÓN ---


# Incluir el router de la API v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint raíz para verificar que la API está viva."""
    return {"status": "API online"}

@app.get("/test-firestore", tags=["Tests"])
def test_firestore_connection():
    """Endpoint para probar la escritura y lectura en Firestore."""
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

