import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import Optional, Any
import os
import json

class FirebaseConfig:
    """Configuración y gestión de Firebase."""
    
    def __init__(self):
        self._firestore_client: Optional[Any] = None
        self._storage_bucket: Optional[Any] = None
        self._initialized: bool = False
    
    def initialize(self):
        """Inicializa las conexiones de Firebase."""
        if self._initialized:
            return
        
        try:
            # Intentar usar credenciales desde variable de entorno (GCP)
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('FIREBASE_CREDENTIALS'):
                # En GCP, usar credenciales por defecto
                firebase_admin.initialize_app({
                    'storageBucket': 'hackaton-a44c8.firebasestorage.app'
                })
            else:
                # En desarrollo local, usar archivo de credenciales
                cred_path = "hackaton-a44c8-f3d9ad76a54d.json"
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': 'hackaton-a44c8.firebasestorage.app'
                    })
                else:
                    # Fallback: intentar inicializar sin credenciales específicas
                    firebase_admin.initialize_app({
                        'storageBucket': 'hackaton-a44c8.firebasestorage.app'
                    })
            
            # Obtener referencias
            self._firestore_client = firestore.client()
            self._storage_bucket = storage.bucket()
            
            self._initialized = True
            print("✅ Conexión con Firestore y Storage establecida.")
            
        except Exception as e:
            print(f"❌ Error al inicializar Firebase: {str(e)}")
            # En caso de error, intentar inicializar sin configuración específica
            try:
                firebase_admin.initialize_app({
                    'storageBucket': 'hackaton-a44c8.firebasestorage.app'
                })
                self._firestore_client = firestore.client()
                self._storage_bucket = storage.bucket()
                self._initialized = True
                print("✅ Conexión con Firebase establecida (modo fallback).")
            except Exception as fallback_error:
                print(f"❌ Error en modo fallback: {str(fallback_error)}")
                raise
    
    @property
    def firestore(self) -> Any:
        """Retorna el cliente de Firestore."""
        if not self._initialized:
            self.initialize()
        assert self._firestore_client is not None
        return self._firestore_client
    
    @property
    def storage_bucket(self) -> Any:
        """Retorna el bucket de Storage."""
        if not self._initialized:
            self.initialize()
        assert self._storage_bucket is not None
        return self._storage_bucket

# Instancia global del gestor de Firebase
firebase_config = FirebaseConfig() 