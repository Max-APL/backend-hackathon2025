# Barrio Fuerte - Motor de Análisis

Backend para análisis de Pymes usando IA con Gemini.

## 🚀 Características

- **Análisis de Pymes**: Análisis inteligente de relevancia y resumen de pymes
- **Integración con Gemini**: Uso de Google Gemini para análisis de texto
- **API REST**: Endpoints para análisis de pymes
- **Firebase Integration**: Almacenamiento en Firestore

## 📋 Endpoints Disponibles

### Análisis de Pymes
- `POST /api/v1/pyme/analyze` - Analizar una pyme y obtener score de relevancia

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd backend-hackathon2025
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar Firebase**
- Colocar el archivo de credenciales `hackaton-a44c8-firebase-adminsdk-fbsvc-9e2a2b3314.json` en el directorio raíz

5. **Ejecutar la aplicación**
```bash
uvicorn app.app:app --reload
```

## 📖 Uso

### Análisis de Pymes

**Endpoint:** `POST /api/v1/pyme/analyze`

**Body:**
```json
{
  "name": "Nombre de la Pyme",
  "description": "Descripción detallada del negocio",
  "industry": "Sector industrial",
  "location": "Ubicación",
  "custom_prompt": "Prompt personalizado (opcional)",
  "popular_times": {
    "monday": [10, 15, 20, 25],
    "tuesday": [12, 18, 22, 28],
    "wednesday": [8, 14, 19, 24],
    "thursday": [11, 16, 21, 26],
    "friday": [13, 17, 23, 29],
    "saturday": [15, 20, 25, 30],
    "sunday": [5, 10, 15, 20]
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "relevance_score": 85,
    "summary": "Resumen conciso de 50 palabras máximo...",
    "custom_prompt_used": false
  }
}
```

## 🔧 Configuración

### Variables de Entorno
- `GOOGLE_API_KEY`: Clave de API de Google Gemini (opcional, se puede configurar en el código)

### Firebase
El proyecto está configurado para usar Firebase Firestore. Asegúrate de tener el archivo de credenciales en el directorio raíz.

## 📁 Estructura del Proyecto

```
backend-hackathon2025/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── api_router.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── pyme_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── pyme_analysis.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py
│   │   └── pyme_service.py
│   ├── utils/
│   │   └── __init__.py
│   └── app.py
├── requirements.txt
├── README.md
└── main.py
```

## 🧪 Testing

### Probar con curl
```bash
curl -X POST "http://localhost:8000/api/v1/pyme/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restaurante El Buen Sabor",
    "description": "Restaurante familiar especializado en comida local con 10 años de experiencia",
    "industry": "Gastronomía",
    "location": "Centro de la ciudad",
    "popular_times": {
      "monday": [10, 15, 20, 25],
      "tuesday": [12, 18, 22, 28],
      "wednesday": [8, 14, 19, 24],
      "thursday": [11, 16, 21, 26],
      "friday": [13, 17, 23, 29],
      "saturday": [15, 20, 25, 30],
      "sunday": [5, 10, 15, 20]
    }
  }'
```

### Probar con Postman
1. Crear una nueva petición POST
2. URL: `http://localhost:8000/api/v1/pyme/analyze`
3. Headers: `Content-Type: application/json`
4. Body: JSON con los datos de la pyme

## 🔍 Health Check

- `GET /` - Verificar que la API está funcionando
- `GET /test-firestore` - Probar conexión con Firebase

## 📝 Notas

- El análisis de popular_times es opcional pero mejora significativamente el score de relevancia
- Los resúmenes están limitados a 50 palabras para máxima concisión
- El sistema usa Google Gemini para análisis inteligente de texto
- Todos los datos se almacenan en Firebase Firestore

## 🚀 Despliegue

Para desplegar en producción:

1. Configurar variables de entorno
2. Usar un servidor WSGI como Gunicorn
3. Configurar proxy reverso (nginx)
4. Asegurar que el archivo de credenciales de Firebase esté disponible

```bash
gunicorn app.app:app -w 4 -k uvicorn.workers.UvicornWorker
```
