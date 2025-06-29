import os
import asyncio
import inspect
from datetime import datetime
import markdown2
import fitz  # PyMuPDF

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ─────────────────────────────
# CONFIGURACIÓN GLOBAL
os.environ["GOOGLE_CLOUD_PROJECT"] = "hackaton-a44c8"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

APP_NAME = "contrato_ai"
USER_ID = "usuario_finanzas"
SESSION_ID = "sesion_finanzas_001"

# ─────────────────────────────
# HERRAMIENTAS
def guardar_pdf(nombre_archivo, contenido_md):
    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontName="Times-Roman", fontSize=11, leading=16))

    blocks = contenido_md.strip().split("\n")  # SIN markdown2.markdown

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


async def generar_contrato(contrato: str) -> str:
    nombre_pdf = f"contratos/Contrato_{datetime.today().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("contratos", exist_ok=True)
    guardar_pdf(nombre_pdf, contrato)
    print(f"✅ Contrato generado: {nombre_pdf}")
    return nombre_pdf

generar_contrato.__signature__ = inspect.Signature([
    inspect.Parameter("contrato", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
])

async def analizar_contrato(nombre_pdf: str) -> str:
    doc = fitz.open(nombre_pdf)
    texto = "\n".join([page.get_text() for page in doc])
    doc.close()
    return texto

analizar_contrato.__signature__ = inspect.Signature([
    inspect.Parameter("nombre_pdf", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
])

# ─────────────────────────────
# AGENTES
def crear_contrato_agent():
    return LlmAgent(
        model="gemini-2.5-flash",
        name="ContratoAgent",
        description="Redacta contratos legales bolivianos.",
        instruction="""
Eres un abogado especializado en derecho civil boliviano. Redacta un contrato legal entre un negocio y un inversor.

Incluye:
- Partes involucradas
- Monto, intereses y condiciones
- Obligaciones y derechos
- Penalidades, garantías, confidencialidad
- Cláusula de no responsabilidad de la app ALAS
- Aplica las leyes bolivianas

NO llames a ninguna función. Solo devuelve el texto del contrato.
""",
        tools=[]  # Sin tools
    )


def crear_analisis_agent():
    return LlmAgent(
        model="gemini-2.5-flash",
        name="AnalisisAgent",
        description="Analiza el contenido de un contrato legal en PDF.",
        instruction="""
Lee el texto completo de un contrato y resume:

- Para el inversor: monto, interés, plazo, garantías
- Para el negocio: obligaciones, penalidades, fechas clave

Devuelve solo un JSON:
{
  "para_inversor": { ... },
  "para_negocio": { ... }
}
""",
        tools=[analizar_contrato],
    )

# ─────────────────────────────
# FLUJO PRINCIPAL
async def main():
    print("📝 Generador y Analizador de Contratos Legales - Bolivia\n")

    negocio = input("🏪 Nombre del negocio: ").strip()
    inversor = input("💼 Nombre del inversor: ").strip()
    monto = input("💰 Monto de la inversión: ").strip()
    condiciones = input("📄 Condiciones (plazo, interés): ").strip()

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # 1. CONTRATO
    contrato_agent = crear_contrato_agent()
    contrato_runner = Runner(
        agent=contrato_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    mensaje_contrato = types.Content(
        role="user",
        parts=[types.Part(text=(
            f"Redacta un contrato legal entre el negocio '{negocio}' y el inversor '{inversor}', "
            f"por un monto de {monto}, bajo estas condiciones: {condiciones}. "
            f"Aplica derecho boliviano y guarda el contrato."
        ))]
    )

    print("\n🤖 Generando contrato legal...\n")
    contenido_md = None

    async for event in contrato_runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=mensaje_contrato
    ):
        if event.content and event.content.parts:
            contenido_md = event.content.parts[0].text
            print("📄 Texto generado:")
            print(contenido_md)
        if event.is_final_response():
            break

    if not contenido_md:
        print("❌ No se pudo obtener el contenido del contrato.")
        return

    pdf_path = await generar_contrato(contenido_md)
    print(f"\n✅ Contrato guardado en: {pdf_path}\n")

    # 2. ANÁLISIS
    analisis_agent = crear_analisis_agent()
    analisis_runner = Runner(
        agent=analisis_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    texto_contrato = await analizar_contrato(pdf_path)

    mensaje_analisis = types.Content(
        role="user",
        parts=[types.Part(text=texto_contrato)]
    )

    print("🔍 Analizando el contrato...\n")
    async for event in analisis_runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=mensaje_analisis
    ):
        if event.content and event.content.parts:
            print("📊 Análisis del contrato:\n")
            print(event.content.parts[0].text)
            break

# ─────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
