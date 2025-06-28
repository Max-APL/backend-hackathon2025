import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import Optional, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

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
            # Verificar si Firebase ya está inicializado
            try:
                firebase_admin.get_app()
                logger.info("✅ Firebase ya inicializado, usando configuración existente")
            except ValueError:
                # Firebase no está inicializado, pero no lo inicializamos aquí
                # porque ya se hizo en app.py
                logger.info("⚠️ Firebase no inicializado en firebase_config, usando configuración de app.py")
            
            # Obtener referencias usando la configuración existente
            self._firestore_client = firestore.client()
            self._storage_bucket = storage.bucket()
            
            self._initialized = True
            print("✅ Conexión con Firestore y Storage establecida.")
            
        except Exception as e:
            print(f"❌ Error al inicializar Firebase config: {str(e)}")
            # No intentar inicializar Firebase aquí, solo manejar el error
            self._initialized = False
    
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