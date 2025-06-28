import uvicorn
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from app.api.v1.api_router import router as api_router

# --- CONFIGURACIÓN DE FIREBASE ---
# Cargar las credenciales desde el archivo de clave de servicio
cred = credentials.Certificate("hackaton-a44c8-firebase-adminsdk-fbsvc-9e2a2b3314.json")

# Inicializar la app de Firebase. Solo se hace una vez.
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

# Obtener una referencia a la base de datos de Firestore
db = firestore.client()
print("✅ Conexión con Firestore establecida.")
# --- FIN DE CONFIGURACIÓN ---

app = FastAPI(
    title="Barrio Fuerte - Motor de Análisis",
    version="0.1.0"
)

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
        doc_ref = db.collection("test_collection").document("test_doc")
        doc_ref.set({"message": "Hola desde FastAPI!"})
        doc = doc_ref.get()
        if doc.exists:
            return {"status": "Éxito", "data_read": doc.to_dict()}
        else:
            raise HTTPException(status_code=500, detail="No se pudo leer el documento después de escribirlo.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Firestore: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

