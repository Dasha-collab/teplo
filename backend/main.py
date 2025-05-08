from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
import io, os, uuid, logging
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_text(pdf, text, fallback_text=None):
    """Безопасное добавление текста с fallback"""
    try:
        pdf.cell(0, 10, txt=text, ln=1, align='C')
        return True
    except:
        if fallback_text:
            pdf.cell(0, 10, txt=fallback_text, ln=1, align='C')
        return False

def generate_pdf(image_path, output_pdf):
    pdf = FPDF(unit="mm", format="A4")
    
    # Шрифты с приоритетом: Noto Sans → DejaVu → Arial Unicode → Helvetica
    font_priority = [
        ("NotoSans", "/opt/render/project/src/backend/fonts/NotoSans-Regular.ttf"),
        ("NotoSans", str(Path(__file__).parent / "fonts" / "NotoSans-Regular.ttf"),
        ("DejaVu", "/opt/render/project/src/backend/fonts/DejaVuSans.ttf"),
        ("ArialUnicode", "/opt/render/project/src/backend/fonts/arialuni.ttf")
    ]
    
    font_set = False
    for font_name, font_path in font_priority:
        try:
            if os.path.exists(font_path):
                pdf.add_font(font_name, "", font_path, uni=True)
                pdf.set_font(font_name, size=12)
                font_set = True
                break
        except Exception as e:
            logger.warning(f"Failed to load font {font_name}: {e}")
    
    if not font_set:
        pdf.set_font("helvetica", size=12)
        logger.warning("Using fallback helvetica font")

    pdf.add_page()
    
    # Добавление изображения
    try:
        pdf.image(image_path, x=15, y=20, w=180)
    except Exception as e:
        logger.error(f"Image error: {e}")
        raise HTTPException(500, detail="Ошибка обработки изображения")

    # Безопасное добавление текста
    if not safe_text(pdf, "Teplo PP - Анализ упаковки", "Teplo PP - Package Analysis"):
        logger.error("Critical font failure")
        raise HTTPException(500, detail="Системная ошибка шрифтов")

    pdf.multi_cell(0, 8, txt="Рекомендации по зоне восприятия:")

    pdf.output(output_pdf)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(400, detail="Поддерживаются только JPG/PNG изображения")
    
    temp_img = f"/tmp/{uuid.uuid4().hex}.jpg"
    temp_pdf = f"/tmp/{uuid.uuid4().hex}.pdf"
    
    try:
        # Обработка изображения
        img = Image.open(io.BytesIO(await file.read()))
        img = img.convert("RGB")
        img.save(temp_img, quality=90)
        
        # Генерация PDF
        generate_pdf(temp_img, temp_pdf)
        
        return FileResponse(
            temp_pdf,
            media_type="application/pdf",
            filename="teplo_analysis.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
    finally:
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try: os.remove(f)
                except: pass

@app.get("/")
async def health_check():
    return {"status": "OK", "version": "1.0.2"}
