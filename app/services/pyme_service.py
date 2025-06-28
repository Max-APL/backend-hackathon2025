import asyncio
from typing import List, Dict, Any, Optional
from app.models.pyme_analysis import PymeAnalysis, PymeStructuredAnalysis
from app.services.gemini_service import GeminiService

class PymeService:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_service = GeminiService(api_key=api_key)
    
    async def analyze_pyme_with_ai(self, pyme_data: PymeAnalysis) -> Dict[str, Any]:
        """
        Analiza una Pyme usando Gemini AI con respuesta estructurada
        """
        try:
            # Convertir PymeAnalysis a dict
            pyme_dict = pyme_data.dict()
            
            # Usar prompt personalizado si se proporciona, sino usar el default
            custom_prompt = pyme_data.prompt
            # Verificar si el prompt personalizado no está vacío y no es solo espacios en blanco
            has_custom_prompt = custom_prompt is not None and custom_prompt.strip() != ""
            
            if has_custom_prompt and custom_prompt is not None:
                prompt = self._build_custom_analysis_prompt(pyme_dict, custom_prompt)
            else:
                prompt = self._build_analysis_prompt(pyme_dict)
            
            # Prompt del sistema
            root_prompt = """
            Eres un analista experto en negocios y evaluación de empresas. 
            Proporciona análisis concisos y puntuaciones basadas en la relevancia del negocio.
            Sé constructivo, positivo y proporciona recomendaciones accionables.
            Usa emojis apropiadamente para hacer el feedback más amigable.
            Mantén el resumen del análisis entre 300-800 caracteres para que sea conciso pero completo.
            """
            
            # Generar análisis estructurado usando la nueva función
            structured_analysis = await self.gemini_service.generate_object_with_schema(
                schema=PymeStructuredAnalysis,
                prompt=prompt,
                model="gemini-2.5-flash",
                temperature=0.7,
                root_prompt=root_prompt
            )
            
            # Retornar resultado combinado
            return {
                "pyme_data": pyme_dict,
                "ai_analysis": {
                    "success": True,
                    "analysis": structured_analysis,
                    "model_used": "gemini-2.5-flash",
                    "message": "Análisis estructurado generado exitosamente",
                    "custom_prompt_used": has_custom_prompt
                }
            }
            
        except Exception as e:
            return {
                "pyme_data": pyme_dict if 'pyme_dict' in locals() else {},
                "ai_analysis": {
                    "success": False,
                    "analysis": None,
                    "model_used": "gemini-2.5-flash",
                    "message": f"Error al analizar Pyme con AI: {str(e)}",
                    "custom_prompt_used": has_custom_prompt if 'has_custom_prompt' in locals() else False
                }
            }
    
    def _build_custom_analysis_prompt(self, pyme_data: Dict[str, Any], custom_prompt: str) -> str:
        """
        Construye el prompt usando el prompt personalizado proporcionado por el usuario
        """
        # Preparar datos de popular_times si están disponibles
        popular_times_info = ""
        popular_times_analysis = ""
        
        if pyme_data.get('popular_times'):
            popular_times = pyme_data['popular_times']
            if popular_times.get('graph_results'):
                # Calcular promedio de ocupación por día
                daily_averages = {}
                total_busyness = 0
                total_active_slots = 0
                
                for day, time_slots in popular_times['graph_results'].items():
                    if time_slots:
                        # Filtrar slots con busyness_score > 0 (horarios abiertos)
                        active_slots = [slot for slot in time_slots if slot.get('busyness_score', 0) > 0]
                        if active_slots:
                            avg_busyness = sum(slot.get('busyness_score', 0) for slot in active_slots) / len(active_slots)
                            daily_averages[day] = round(avg_busyness, 1)
                            total_busyness += sum(slot.get('busyness_score', 0) for slot in active_slots)
                            total_active_slots += len(active_slots)
                
                # Calcular promedio general de ocupación
                overall_avg = round(total_busyness / total_active_slots, 1) if total_active_slots > 0 else 0
                
                # Encontrar horarios pico (muy ocupados)
                peak_hours = []
                for day, time_slots in popular_times['graph_results'].items():
                    for slot in time_slots:
                        if slot.get('busyness_score', 0) >= 80:  # Muy ocupado
                            peak_hours.append(f"{day} {slot.get('time', '')} ({slot.get('busyness_score', 0)}%)")
                
                # Encontrar días más ocupados
                sorted_days = sorted(daily_averages.items(), key=lambda x: x[1], reverse=True)
                busiest_days = sorted_days[:3]  # Top 3 días más ocupados
                
                # Encontrar horarios más ocupados por día
                peak_times_by_day = {}
                for day, time_slots in popular_times['graph_results'].items():
                    if time_slots:
                        max_slot = max(time_slots, key=lambda x: x.get('busyness_score', 0))
                        if max_slot.get('busyness_score', 0) > 0:
                            peak_times_by_day[day] = {
                                'time': max_slot.get('time', ''),
                                'score': max_slot.get('busyness_score', 0),
                                'info': max_slot.get('info', '')
                            }
                
                popular_times_info = f"""
                
                DATOS DE HORARIOS POPULARES:
                - Promedio general de ocupación: {overall_avg}%
                - Promedio por día: {daily_averages}
                - Días más ocupados: {[f"{day} ({score}%)" for day, score in busiest_days]}
                - Horarios pico (muy ocupados): {peak_hours[:8]}  # Top 8
                - Horario más ocupado por día: {peak_times_by_day}
                - Información en tiempo real: {popular_times.get('live_hash', {}).get('info', 'No disponible')}
                """
                
                # Análisis específico de popular_times para el prompt
                popular_times_analysis = f"""
                
                ANÁLISIS ESPECÍFICO DE HORARIOS Y DEMANDA:
                
                **Patrones de Ocupación:**
                - Ocupación promedio general: {overall_avg}%
                - Días de mayor actividad: {[day for day, _ in busiest_days]}
                - Días de menor actividad: {[day for day, _ in sorted_days[-3:]]}
                
                **Horarios Pico Identificados:**
                {chr(10).join([f"- {peak}" for peak in peak_hours[:5]])}
                
                **Análisis de Rentabilidad por Horario:**
                - Horarios de mayor demanda: {[f"{day} {data['time']} ({data['score']}%)" for day, data in list(peak_times_by_day.items())[:3]]}
                - Horarios de menor demanda: {[f"{day} {data['time']} ({data['score']}%)" for day, data in list(peak_times_by_day.items())[-3:]]}
                
                **Implicaciones para el Negocio:**
                - El negocio tiene una demanda {overall_avg}% de ocupación promedio
                - Los días más rentables son: {[day for day, _ in busiest_days]}
                - Los horarios pico sugieren una base de clientes estable
                - Hay oportunidades de optimización en días de menor actividad
                """
        
        prompt = f"""
        {custom_prompt}

        DATOS DEL NEGOCIO:
        {{
            "address": "{pyme_data.get('address', '')}",
            "description": "{pyme_data.get('description', '')}",
            "id": "{pyme_data.get('id', '')}",
            "phone": "{pyme_data.get('phone', '')}",
            "price": {pyme_data.get('price', 0)},
            "rating": {pyme_data.get('rating', 0.0)},
            "reviews": {pyme_data.get('reviews', 0)},
            "reviews_data": {pyme_data.get('reviews_data', [])},
            "title": "{pyme_data.get('title', '')}",
            "type": "{pyme_data.get('type', '')}",
            "website": "{pyme_data.get('website', '')}"
        }}{popular_times_info}{popular_times_analysis}

        IMPORTANTE: 
        - Responde ÚNICAMENTE con el JSON estructurado según el esquema proporcionado.
        - El resumen del análisis debe ser ULTRA CONCISO (máximo 50 palabras).
        - Si hay datos de horarios populares, inclúyelos en tu análisis.
        - Los datos de popular_times son FUNDAMENTALES para evaluar la relevancia.
        - Usa los patrones de ocupación para justificar el score de relevancia.
        - **MANTÉN EL RESUMEN ULTRA BREVE Y DIRECTO AL PUNTO**.
        """
        
        return prompt
    
    def _build_analysis_prompt(self, pyme_data: Dict[str, Any]) -> str:
        """
        Construye el prompt para el análisis de Pyme con score de relevancia único
        """
        # Preparar datos de popular_times si están disponibles
        popular_times_info = ""
        popular_times_analysis = ""
        
        if pyme_data.get('popular_times'):
            popular_times = pyme_data['popular_times']
            if popular_times.get('graph_results'):
                # Calcular promedio de ocupación por día
                daily_averages = {}
                total_busyness = 0
                total_active_slots = 0
                
                for day, time_slots in popular_times['graph_results'].items():
                    if time_slots:
                        # Filtrar slots con busyness_score > 0 (horarios abiertos)
                        active_slots = [slot for slot in time_slots if slot.get('busyness_score', 0) > 0]
                        if active_slots:
                            avg_busyness = sum(slot.get('busyness_score', 0) for slot in active_slots) / len(active_slots)
                            daily_averages[day] = round(avg_busyness, 1)
                            total_busyness += sum(slot.get('busyness_score', 0) for slot in active_slots)
                            total_active_slots += len(active_slots)
                
                # Calcular promedio general de ocupación
                overall_avg = round(total_busyness / total_active_slots, 1) if total_active_slots > 0 else 0
                
                # Encontrar horarios pico (muy ocupados)
                peak_hours = []
                for day, time_slots in popular_times['graph_results'].items():
                    for slot in time_slots:
                        if slot.get('busyness_score', 0) >= 80:  # Muy ocupado
                            peak_hours.append(f"{day} {slot.get('time', '')} ({slot.get('busyness_score', 0)}%)")
                
                # Encontrar días más ocupados
                sorted_days = sorted(daily_averages.items(), key=lambda x: x[1], reverse=True)
                busiest_days = sorted_days[:3]  # Top 3 días más ocupados
                
                # Encontrar horarios más ocupados por día
                peak_times_by_day = {}
                for day, time_slots in popular_times['graph_results'].items():
                    if time_slots:
                        max_slot = max(time_slots, key=lambda x: x.get('busyness_score', 0))
                        if max_slot.get('busyness_score', 0) > 0:
                            peak_times_by_day[day] = {
                                'time': max_slot.get('time', ''),
                                'score': max_slot.get('busyness_score', 0),
                                'info': max_slot.get('info', '')
                            }
                
                popular_times_info = f"""
                
                DATOS DE HORARIOS POPULARES:
                - Promedio general de ocupación: {overall_avg}%
                - Promedio por día: {daily_averages}
                - Días más ocupados: {[f"{day} ({score}%)" for day, score in busiest_days]}
                - Horarios pico (muy ocupados): {peak_hours[:8]}  # Top 8
                - Horario más ocupado por día: {peak_times_by_day}
                - Información en tiempo real: {popular_times.get('live_hash', {}).get('info', 'No disponible')}
                """
                
                # Análisis específico de popular_times para el prompt
                popular_times_analysis = f"""
                
                ANÁLISIS ESPECÍFICO DE HORARIOS Y DEMANDA:
                
                **Patrones de Ocupación:**
                - Ocupación promedio general: {overall_avg}%
                - Días de mayor actividad: {[day for day, _ in busiest_days]}
                - Días de menor actividad: {[day for day, _ in sorted_days[-3:]]}
                
                **Horarios Pico Identificados:**
                {chr(10).join([f"- {peak}" for peak in peak_hours[:5]])}
                
                **Análisis de Rentabilidad por Horario:**
                - Horarios de mayor demanda: {[f"{day} {data['time']} ({data['score']}%)" for day, data in list(peak_times_by_day.items())[:3]]}
                - Horarios de menor demanda: {[f"{day} {data['time']} ({data['score']}%)" for day, data in list(peak_times_by_day.items())[-3:]]}
                
                **Implicaciones para el Negocio:**
                - El negocio tiene una demanda {overall_avg}% de ocupación promedio
                - Los días más rentables son: {[day for day, _ in busiest_days]}
                - Los horarios pico sugieren una base de clientes estable
                - Hay oportunidades de optimización en días de menor actividad
                """
        
        prompt = f"""
        Analiza el siguiente negocio y proporciona una evaluación de relevancia:

        DATOS DEL NEGOCIO:
        {{
            "address": "{pyme_data.get('address', '')}",
            "description": "{pyme_data.get('description', '')}",
            "id": "{pyme_data.get('id', '')}",
            "phone": "{pyme_data.get('phone', '')}",
            "price": {pyme_data.get('price', 0)},
            "rating": {pyme_data.get('rating', 0.0)},
            "reviews": {pyme_data.get('reviews', 0)},
            "reviews_data": {pyme_data.get('reviews_data', [])},
            "title": "{pyme_data.get('title', '')}",
            "type": "{pyme_data.get('type', '')}",
            "website": "{pyme_data.get('website', '')}"
        }}{popular_times_info}{popular_times_analysis}

        INSTRUCCIONES DE ANÁLISIS:

        Evalúa la **relevancia** del negocio en una escala del 0 al 100 basándote en:

        1. **Calificación y Reputación** (30% del score):
           - Calificación promedio y número de reseñas
           - Calidad del feedback de los clientes
           - Consistencia en la satisfacción del cliente

        2. **Análisis de Horarios y Demanda** (25% del score):
           - Patrones de ocupación y horarios pico
           - Consistencia en la demanda a lo largo de la semana
           - Horarios de mayor actividad y rentabilidad
           - Análisis de días más y menos ocupados
           - Si no hay datos de horarios, asigna 0 puntos a esta categoría

        3. **Presencia y Visibilidad** (20% del score):
           - Información de contacto completa
           - Sitio web funcional
           - Descripción clara y atractiva

        4. **Competitividad y Posicionamiento** (15% del score):
           - Precio competitivo para el tipo de negocio
           - Diferenciación en el mercado
           - Tipo de negocio y demanda

        5. **Potencial de Crecimiento** (10% del score):
           - Oportunidades de mejora identificadas
           - Capacidad de escalabilidad
           - Fortalezas del negocio

        **Cálculo del Score:**
        - Comienza con un puntaje base de **70 puntos**
        - Ajusta según los criterios anteriores
        - Si no hay datos de popular_times, asigna 0 puntos a esa categoría
        - Los datos de horarios son CRÍTICOS para evaluar la demanda real
        - Asegúrate de que el puntaje final esté entre **0 y 100**

        **Resumen del Análisis:**
        - Proporciona un resumen ULTRA CONCISO de máximo 50 palabras
        - Incluye SOLO la fortaleza más importante del negocio
        - Identifica la oportunidad de mejora más crítica
        - Da UNA recomendación específica y accionable
        - Usa un tono positivo y constructivo
        - Incluye emojis apropiados (máximo 1-2)
        - **Menciona específicamente los patrones de horarios y su impacto en la relevancia**
        - Analiza cómo los horarios populares afectan la rentabilidad
        - Sugiere estrategias basadas en los datos de ocupación
        - **MANTÉN EL RESUMEN ULTRA BREVE Y DIRECTO AL PUNTO**

        **Formato de Respuesta:**
        - "relevance_score": puntuación de 0 a 100
        - "analysis_summary": resumen completo del análisis (máximo 800 caracteres)

        IMPORTANTE: 
        - Responde ÚNICAMENTE con el JSON estructurado según el esquema proporcionado.
        - Los datos de popular_times son FUNDAMENTALES para el análisis.
        - Si hay datos de horarios, úsalos para justificar el score.
        """
        
        return prompt