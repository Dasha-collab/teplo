from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
import io, os, uuid, logging
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройка CORS (исправлены скобки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pdf(image_path, output_pdf):
    pdf = FPDF(unit="mm", format="A4")
    
    try:
        font_path = Path(__file__).parent / "fonts" / "NotoSans-Regular.ttf"
        if font_path.exists():
            pdf.add_font("NotoSans", "", str(font_path), uni=True)
            pdf.set_font("NotoSans", size=12)
        else:
            pdf.set_font("Arial", size=12)
    except Exception as e:
        logger.error(f"Font error: {e}")
        pdf.set_font("helvetica", size=12)

    pdf.add_page()
    pdf.image(image_path, x=15, y=20, w=180)
    pdf.cell(0, 10, txt="Teplo PP - Анализ упаковки", ln=1, align="C")
    pdf.multi_cell(0, 8, txt="Рекомендации по зоне восприятия:")
    pdf.output(output_pdf)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(400, detail="Только JPG/PNG изображения")
    
    temp_img = f"/tmp/{uuid.uuid4().hex}.jpg"
    temp_pdf = f"/tmp/{uuid.uuid4().hex}.pdf"
    
    try:
        img = Image.open(io.BytesIO(await file.read()))
        img = img.convert("RGB")
        img.save(temp_img, quality=85)
        
        generate_pdf(temp_img, temp_pdf)
        
        return FileResponse(
            temp_pdf,
            media_type="application/pdf",
            filename="teplo_analysis.pdf"
        )
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
    finally:
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try: os.remove(f)
                except: pass

@app.get("/")
async def health_check():
    return {"status": "OK"}
