import uvicorn
from fastapi import FastAPI, HTTPException
from app.core.firebase_config import firebase_config
from app.api.v1.api_router import api_router

# Inicializar Firebase
firebase_config.initialize()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

