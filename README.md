# Backend Hackathon 2025 - Análisis de Pymes con IA

Este proyecto proporciona un sistema de análisis de Pymes usando Gemini AI con respuestas estructuradas en JSON.

## 🚀 Características

- **Análisis Simplificado**: Score de relevancia único y resumen completo
- **Gemini AI Integration**: Uso de Gemini 2.5 Flash para análisis inteligente
- **FastAPI**: API REST moderna y rápida
- **Validación de Datos**: Esquemas Pydantic para validación automática
- **Prompts Personalizables**: Envía tu propio prompt para análisis específicos

## 📊 Sistema de Análisis

El sistema analiza Pymes con un **score de relevancia único** basado en:

### 🎯 Criterios de Evaluación (Score 0-100)

1. **Calificación y Reputación** (40% del score):
   - Calificación promedio y número de reseñas
   - Calidad del feedback de los clientes
   - Consistencia en la satisfacción del cliente

2. **Presencia y Visibilidad** (30% del score):
   - Información de contacto completa
   - Sitio web funcional
   - Descripción clara y atractiva

3. **Competitividad y Posicionamiento** (20% del score):
   - Precio competitivo para el tipo de negocio
   - Diferenciación en el mercado
   - Tipo de negocio y demanda

4. **Potencial de Crecimiento** (10% del score):
   - Oportunidades de mejora identificadas
   - Capacidad de escalabilidad
   - Fortalezas del negocio

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd backend-hackathon2025

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key de Gemini
export GEMINI_API_KEY="tu-api-key-aqui"
```

## 🚀 Uso

### Iniciar el servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### Endpoint Disponible

#### Análisis con IA
```http
POST /pyme/analyze-ai
```

### Ejemplo de Uso

```python
import asyncio
from app.services.pyme_service import PymeService
from app.models.pyme_analysis import PymeAnalysis

async def analizar_pyme():
    # Datos de la Pyme
    datos_pyme = PymeAnalysis(
        address="8R8W+MJH, Unnamed Road, Santa Cruz de la Sierra, Bolivia",
        description="",
        id="G2zelR8vieI22RjMHTXN",
        phone="+591 75001088",
        price=30,
        rating=4.9,
        reviews=7,
        reviews_data=["", "", "", "", "", "", ""],
        title="El Gauchito",
        type="Restaurant",
        website=""
    )
    
    # Crear servicio y analizar
    service = PymeService()
    resultado = await service.analyze_pyme_with_ai(datos_pyme)
    
    # Mostrar resultados
    if resultado["ai_analysis"]["success"]:
        analisis = resultado["ai_analysis"]["analysis"]
        print(f"Score de Relevancia: {analisis.relevance_score}/100")
        print(f"Resumen: {analisis.analysis_summary}")

# Ejecutar
asyncio.run(analizar_pyme())
```

### Ejemplo con Prompt Personalizado

```python
# Datos con prompt personalizado
datos_pyme = PymeAnalysis(
    address="8R8W+MJH, Unnamed Road, Santa Cruz de la Sierra, Bolivia",
    description="",
    id="G2zelR8vieI22RjMHTXN",
    phone="+591 75001088",
    price=30,
    rating=4.9,
    reviews=7,
    reviews_data=["", "", "", "", "", "", ""],
    title="El Gauchito",
    type="Restaurant",
    website="",
    prompt="""
    Analiza este restaurante boliviano enfocándote especialmente en:
    
    1. **Potencial de crecimiento en el mercado local**
    2. **Oportunidades de expansión**
    3. **Análisis de la competencia en Santa Cruz**
    4. **Recomendaciones específicas para restaurantes en Bolivia**
    
    Evalúa la relevancia considerando el contexto boliviano.
    """
)

# El análisis usará tu prompt personalizado
resultado = await service.analyze_pyme_with_ai(datos_pyme)
```

### Ejemplo de Respuesta

```json
{
  "pyme_data": {
    "address": "8R8W+MJH, Unnamed Road, Santa Cruz de la Sierra, Bolivia",
    "title": "El Gauchito",
    "rating": 4.9,
    "reviews": 7,
    "price": 30,
    "type": "Restaurant"
  },
  "ai_analysis": {
    "success": true,
    "analysis": {
      "relevance_score": 85,
      "analysis_summary": "¡Excelente negocio con gran potencial! 🎉 El restaurante 'El Gauchito' demuestra una sólida base con una calificación excepcional de 4.9/5.0, lo que indica alta satisfacción del cliente. Aunque tiene solo 7 reseñas, la calidad del feedback es muy positiva. El precio de $30 está bien posicionado para un restaurante en Santa Cruz. Para mejorar la relevancia, se recomienda: 1) Crear un sitio web profesional para aumentar la presencia online, 2) Implementar estrategias para generar más reseñas, 3) Agregar una descripción detallada del negocio y sus especialidades. El negocio tiene excelentes fundamentos para crecer en el mercado local boliviano. 🌟"
    },
    "custom_prompt_used": false
  }
}
```

## 📋 Estructura de Datos

### Entrada (PymeAnalysis)
```python
{
    "address": str,        # Dirección del negocio
    "description": str,    # Descripción del negocio
    "id": str,            # ID único
    "phone": str,         # Número de teléfono
    "price": int,         # Precio del servicio/producto
    "rating": float,      # Calificación promedio (0-5)
    "reviews": int,       # Número de reseñas
    "reviews_data": List[str],  # Datos de las reseñas
    "title": str,         # Título del negocio
    "type": str,          # Tipo de negocio
    "website": str,       # Sitio web
    "prompt": str         # Prompt personalizado (opcional)
}
```

### Salida (Análisis Estructurado)
```python
{
    "relevance_score": int,    # Puntuación de relevancia 0-100
    "analysis_summary": str    # Resumen completo del análisis
}
```

## 🎯 Prompts Personalizados

Puedes enviar un `prompt` personalizado en los datos JSON para personalizar el análisis:

### Ejemplos de Prompts Específicos

#### 1. Análisis de Mercado Local
```json
{
  "prompt": "Analiza este negocio enfocándote en el mercado local de Santa Cruz, oportunidades de crecimiento, y competencia en la zona."
}
```

#### 2. Análisis de Marketing Digital
```json
{
  "prompt": "Evalúa desde una perspectiva de marketing digital. Analiza presencia online, estrategias de marketing, y oportunidades en redes sociales."
}
```

#### 3. Análisis Financiero
```json
{
  "prompt": "Analiza desde una perspectiva financiera. Evalúa modelo de negocio, potencial de escalabilidad, y recomendaciones para optimizar costos."
}
```

#### 4. Análisis de Competencia
```json
{
  "prompt": "Compara este negocio con la competencia local. Identifica ventajas competitivas y áreas de mejora para diferenciarse."
}
```

## 🧪 Pruebas

### Usar el script de ejemplo
```bash
python ejemplo-pyme-analisis.py
```

### Usar el archivo HTTP
```bash
# Con VS Code REST Client o similar
# Abrir test-pyme-analysis.http y ejecutar las pruebas
```

### Ejemplos de Pruebas HTTP

#### Análisis con Prompt por Defecto
```http
POST http://localhost:8000/pyme/analyze-ai
Content-Type: application/json

{
  "address": "8R8W+MJH, Unnamed Road, Santa Cruz de la Sierra, Bolivia",
  "description": "",
  "id": "G2zelR8vieI22RjMHTXN",
  "phone": "+591 75001088",
  "price": 30,
  "rating": 4.9,
  "reviews": 7,
  "reviews_data": ["", "", "", "", "", "", ""],
  "title": "El Gauchito",
  "type": "Restaurant",
  "website": ""
}
```

#### Análisis con Prompt Personalizado
```http
POST http://localhost:8000/pyme/analyze-ai
Content-Type: application/json

{
  "address": "8R8W+MJH, Unnamed Road, Santa Cruz de la Sierra, Bolivia",
  "description": "",
  "id": "G2zelR8vieI22RjMHTXN",
  "phone": "+591 75001088",
  "price": 30,
  "rating": 4.9,
  "reviews": 7,
  "reviews_data": ["", "", "", "", "", "", ""],
  "title": "El Gauchito",
  "type": "Restaurant",
  "website": "",
  "prompt": "Analiza este restaurante boliviano enfocándote en el potencial de crecimiento en el mercado local de Santa Cruz."
}
```

## 🔧 Configuración

### Variables de Entorno
```bash
GEMINI_API_KEY=tu-api-key-de-gemini
```

### Modelos de IA Disponibles
- `gemini-2.5-flash` (recomendado)
- `gemini-1.5-flash`
- `gemini-1.5-pro`

## 📈 Interpretación de Puntuaciones

- **90-100**: Excelente - Relevancia muy alta
- **80-89**: Muy bien - Buena relevancia en el mercado
- **70-79**: Regular - Relevancia moderada
- **60-69**: Necesita mejoras - Relevancia baja
- **0-59**: Baja relevancia - Se requieren mejoras significativas

## 💡 Tips para Prompts Efectivos

1. **Sé Específico**: Define claramente qué aspectos quieres analizar
2. **Contexto Local**: Incluye información sobre el mercado local
3. **Enfoque Sectorial**: Especifica el tipo de análisis (marketing, financiero, etc.)
4. **Objetivos Claros**: Define qué quieres lograr con el análisis
5. **Mantén la Simplicidad**: El prompt debe generar un score de relevancia y resumen

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte, email: soporte@hackathon2025.com o crear un issue en el repositorio.
