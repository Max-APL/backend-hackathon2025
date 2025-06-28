from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TimeSlot(BaseModel):
    """Modelo para un horario específico"""
    time: str = Field(..., description="Hora del día (ej: '6 AM', '12 PM')")
    busyness_score: int = Field(..., ge=0, le=100, description="Puntuación de ocupación de 0 a 100")
    info: Optional[str] = Field(default=None, description="Información adicional sobre el horario")

class DaySchedule(BaseModel):
    """Modelo para el horario de un día específico"""
    day: str = Field(..., description="Día de la semana")
    time_slots: List[TimeSlot] = Field(..., description="Lista de horarios del día")

class PopularTimes(BaseModel):
    """Modelo para datos de horarios populares"""
    graph_results: Dict[str, List[TimeSlot]] = Field(..., description="Resultados por día de la semana")
    live_hash: Optional[Dict[str, str]] = Field(default=None, description="Información en tiempo real")

class PymeAnalysis(BaseModel):
    """Modelo para datos básicos de Pyme"""
    address: str = Field(..., description="Dirección del negocio")
    description: str = Field(..., description="Descripción del negocio")
    id: str = Field(..., description="ID único del negocio")
    phone: str = Field(..., description="Número de teléfono")
    price: int = Field(..., description="Precio del servicio/producto")
    rating: float = Field(..., description="Calificación promedio")
    reviews: int = Field(..., description="Número de reseñas")
    reviews_data: List[str] = Field(..., description="Datos de las reseñas")
    title: str = Field(..., description="Título del negocio")
    type: str = Field(..., description="Tipo de negocio")
    website: str = Field(..., description="Sitio web del negocio")
    prompt: Optional[str] = Field(default=None, description="Prompt personalizado para el análisis (opcional)")
    popular_times: Optional[PopularTimes] = Field(default=None, description="Datos de horarios populares (opcional)")

class CategoryScore(BaseModel):
    """Modelo para puntuación de categoría individual"""
    score: int = Field(..., ge=0, le=100, description="Puntuación de 0 a 100")
    description: str = Field(..., max_length=500, description="Justificación de la puntuación")

class SkillsAnalysis(BaseModel):
    """Modelo para análisis de habilidades"""
    hard: List[str] = Field(..., description="Habilidades técnicas principales")
    soft: List[str] = Field(..., description="Habilidades sociales principales")

class RedactionAnalysis(BaseModel):
    """Modelo para análisis de redacción"""
    score: int = Field(..., ge=0, le=100, description="Puntuación de 0 a 100")
    description: str = Field(..., max_length=500, description="Feedback de redacción")
    skills: SkillsAnalysis = Field(..., description="Análisis de habilidades")

class PymeStructuredAnalysis(BaseModel):
    """Modelo para análisis estructurado de Pyme con score de relevancia y resumen"""
    relevance_score: int = Field(..., ge=0, le=100, description="Puntuación de relevancia de 0 a 100")
    analysis_summary: str = Field(..., max_length=2000, description="Resumen completo del análisis") 