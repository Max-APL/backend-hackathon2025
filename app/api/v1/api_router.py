from fastapi import APIRouter

api_router = APIRouter()

# Incluir routers de forma opcional para evitar errores de startup
try:
    from app.controllers.pyme_controller import router as pyme_router
    api_router.include_router(pyme_router)
    print("✅ Pyme router incluido")
except Exception as e:
    print(f"⚠️ Error incluyendo pyme router: {e}")

try:
    from app.api.v1.endpoints import peques
    api_router.include_router(peques.router, tags=["Peques"])
    print("✅ Peques router incluido")
except Exception as e:
    print(f"⚠️ Error incluyendo peques router: {e}")

try:
    from app.api.v1.endpoints import storage
    api_router.include_router(storage.router, prefix="/storage", tags=["Storage"])
    print("✅ Storage router incluido")
except Exception as e:
    print(f"⚠️ Error incluyendo storage router: {e}")

