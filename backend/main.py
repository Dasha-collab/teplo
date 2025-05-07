from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image
import io, os, uuid
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

def create_pdf_report(image_path, output_pdf):
    """Создает PDF отчет с изображением"""
    pdf = FPDF(unit="mm", format="A4")
    
    # Установка шрифта с поддержкой кириллицы
    try:
        font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
        pdf.add_font("DejaVu", "", str(font_path), uni=True)
        pdf.set_font("DejaVu", size=12)
    except:
        pdf.set_font("Arial", size=12)
    
    pdf.add_page()
    pdf.image(image_path, x=15, y=20, w=180)
    pdf.cell(0, 10, txt="Teplo PP - Анализ упаковки", ln=1, align="C")
    pdf.multi_cell(0, 8, txt="Рекомендации:")
    pdf.multi_cell(0, 8, txt="- Проверьте центральную зону")
    pdf.output(output_pdf)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    """Обработка загруженного изображения"""
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(400, detail="Только JPG/PNG изображения")
    
    temp_img = f"/tmp/{uuid.uuid4().hex}.jpg"
    temp_pdf = f"/tmp/{uuid.uuid4().hex}.pdf"
    
    try:
        # Сохранение изображения
        img = Image.open(io.BytesIO(await file.read()))
        img = img.convert("RGB")
        img.save(temp_img, quality=85)
        
        # Создание PDF
        create_pdf_report(temp_img, temp_pdf)
        
        return FileResponse(
            temp_pdf,
            media_type="application/pdf",
            filename="packaging_analysis.pdf"
        )
    except Exception as e:
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
    return {"status": "OK", "message": "Сервис анализа упаковки работает"}
