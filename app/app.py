import os
import asyncio
import inspect
import base64
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import re
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import markdown2

# ---------- CONFIGURACIÓN FIREBASE ----------
cred = credentials.Certificate("hackaton-a44c8-firebase-adminsdk-fbsvc-9e2a2b3314.json")
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)
db = firestore.client()
print("✅ Conexión con Firestore establecida.")
# --------------------------------------------

# ---------- CONFIGURACIÓN ADK / GEMINI ----------
os.environ["GOOGLE_CLOUD_PROJECT"] = "hackaton-a44c8"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
APP_NAME = "contrato_ai"
USER_ID = "usuario_finanzas"
SESSION_ID = "sesion_finanzas_001"
# -----------------------------------------------

app = FastAPI(
    title="Barrio Fuerte - Motor de Análisis",
    version="0.1.0"
)

# ---------- MODELOS ----------
class ContratoInput(BaseModel):
    negocio: str
    inversor: str
    monto: str
    condiciones: str
# ----------------------------

# ---------- UTILIDADES PDF ----------
def limpiar_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")

def guardar_pdf(nombre_archivo, contenido_md):
    contenido_html = markdown2.markdown(contenido_md)
    contenido_limpio = limpiar_html(contenido_html)

    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontName="Times-Roman", fontSize=11, leading=16))

    blocks = contenido_limpio.strip().split("\n")
    story = []

    for block in blocks:
        if block.strip():
            story.append(Paragraph(block.strip(), styles["Justify"]))
            story.append(Spacer(1, 12))

    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Fecha: {datetime.today().strftime('%d/%m/%Y')}", styles["Normal"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph("___________________________", styles["Normal"]))
    story.append(Paragraph("Firma del Inversor", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("___________________________", styles["Normal"]))
    story.append(Paragraph("Firma del Representante del Negocio", styles["Normal"]))

    doc.build(story)
# --------------------------------------

# ---------- HERRAMIENTA ADK ----------
async def generar_contrato(contrato: str) -> str:
    nombre_pdf = f"contratos/Contrato_{datetime.today().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("contratos", exist_ok=True)
    guardar_pdf(nombre_pdf, contrato)
    return nombre_pdf

generar_contrato.__signature__ = inspect.Signature(
    parameters=[inspect.Parameter("contrato", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)]
)

async def initialize_runner():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    contrato_agent = LlmAgent(
        model="gemini-2.5-flash",
        name="ContratoAgent",
        description="Genera contratos en PDF a partir de los datos proporcionados.",
        instruction="""
Eres un abogado experto en derecho civil boliviano. Tu tarea es redactar un contrato legal profesional entre un negocio y un inversor.

⚠️ No valides ni consultes nada. Recibirás nombres, monto y condiciones. Redacta el contrato legal completo en texto plano y llama a la herramienta 'generar_contrato(contrato)' con el contenido final.

Incluye cláusulas de:
- Definiciones de partes
- Obligaciones y derechos
- Intereses y plazos
- Garantías, incumplimiento y penalidades
- Clausula de no responsabilidad de la app ALAS (intermediaria)
- Límites legales (hasta 20,000 Bs)
- Confidencialidad de datos

El contrato debe ser aplicable en Bolivia y estar listo para firmar.
""",
        tools=[generar_contrato],
    )

    return Runner(agent=contrato_agent, app_name=APP_NAME, session_service=session_service)
# --------------------------------------

# ---------- ENDPOINTS ----------
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API online"}

@app.get("/test-firestore", tags=["Tests"])
def test_firestore_connection():
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

@app.get("/test-webhook", tags=["Tests"])
def test_webhook():
    try:
        url = "https://maxpasten.app.n8n.cloud/webhook-test/f182d304-1d67-4798-bd58-24dc84caec48"
        response = requests.get(url)
        return {
            "status_code": response.status_code,
            "response_text": response.text,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al probar webhook: {str(e)}")

@app.post("/generar-contrato", tags=["Contratos"])
async def generar_contrato_endpoint(data: ContratoInput):
    runner = await initialize_runner()

    mensaje = (
        f"Redacta un contrato legal profesional entre el negocio '{data.negocio}' y el inversor '{data.inversor}', "
        f"por un monto de {data.monto}, bajo estas condiciones: {data.condiciones}. "
        f"Aplica derecho boliviano. Devuelve solo el contrato, sin explicaciones."
    )

    user_message = types.Content(role="user", parts=[types.Part(text=mensaje)])

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message
        ):
            if event.is_final_response():
                texto = event.content.parts[0].text
                pdf_path = await generar_contrato(texto)

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                encoded = base64.b64encode(pdf_bytes).decode("utf-8")

                return {
                    "nombre_archivo": os.path.basename(pdf_path),
                    "pdf_base64": encoded,
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación del contrato: {str(e)}")
# --------------------------------------

# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
# ---------------------------------
