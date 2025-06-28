import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import Optional, Any

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
        
        # Cargar las credenciales desde el archivo de clave de servicio
        cred = credentials.Certificate("hackaton-a44c8-firebase-adminsdk-fbsvc-9e2a2b3314.json")
        
        # Inicializar la app de Firebase. Solo se hace una vez.
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'hackaton-a44c8.firebasestorage.app'
            })
        
        # Obtener referencias
        self._firestore_client = firestore.client()
        self._storage_bucket = storage.bucket()
        
        self._initialized = True
        print("✅ Conexión con Firestore y Storage establecida.")
    
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

# Instancia global
firebase_config = FirebaseConfig() 