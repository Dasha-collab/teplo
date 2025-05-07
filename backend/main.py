from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import io, os, uuid, logging
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pdf(image_path, output_pdf):
    pdf = FPDF(unit="mm", format="A4")
    
    try:
        # Попытка использовать DejaVu
        font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
        if font_path.exists():
            pdf.add_font("DejaVu", "", str(font_path), uni=True)
            pdf.set_font("DejaVu", size=12)
        else:
            # Fallback на Noto Sans
            noto_path = Path(__file__).parent / "fonts" / "NotoSans-Regular.ttf"
            if noto_path.exists():
                pdf.add_font("NotoSans", "", str(noto_path), uni=True)
                pdf.set_font("NotoSans", size=12)
            else:
                # Последний fallback на Arial Unicode
                pdf.add_font("ArialUnicode", "", "arialuni.ttf", uni=True)
                pdf.set_font("ArialUnicode", size=12)
    except Exception as e:
        logger.error(f"Font error: {e}")
        pdf.set_font("Arial", size=12)
    
    pdf.add_page()
    pdf.image(image_path, x=15, y=20, w=180)
    
    # Текст с поддержкой Unicode
    pdf.cell(0, 10, txt="Teplo PP - Анализ упаковки", ln=1, align="C")
    pdf.multi_cell(0, 10, txt="Рекомендации по зоне восприятия:")
    
    pdf.output(output_pdf)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(400, detail="Только JPG/PNG изображения")
    
    temp_img = f"/tmp/{uuid.uuid4().hex}.jpg"
    temp_pdf = f"/tmp/{uuid.uuid4().hex}.pdf"
    
    try:
        # Обработка изображения
        img = Image.open(io.BytesIO(await file.read()))
        img = img.convert("RGB")
        img.save(temp_img, quality=85)
        
        # Генерация PDF
        generate_pdf(temp_img, temp_pdf)
        
        return FileResponse(
            temp_pdf,
            media_type="application/pdf",
            filename="teplo_analysis.pdf"
        )
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
    finally:
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try: 
                    os.remove(f)
                except:
                    pass

@app.get("/")
async def health_check():
    return {"status": "OK"}
