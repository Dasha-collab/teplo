from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

def safe_text(pdf, text, max_width=180):
    """Обеспечивает безопасное добавление текста с поддержкой Unicode"""
    try:
        if pdf.get_string_width(text) > max_width:
            text = text[:int(max_width/5)] + "..."
        pdf.cell(0, 10, txt=text, ln=1, align="C")
    except:
        pdf.cell(0, 10, txt="Teplo Report", ln=1, align="C")

def generate_pdf(image_path, output_pdf):
    pdf = FPDF(unit="mm", format="A4")
    
    # Установка Unicode-шрифта (3 уровня резервирования)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        str(Path(__file__).parent / "fonts" / "DejaVuSans.ttf",  # Локальный
        str(Path(__file__).parent / "fonts" / "arial-unicode-ms.ttf"  # Windows
    ]
    
    for font_path in font_paths:
        try:
            pdf.add_font("UnicodeFont", "", font_path, uni=True)
            pdf.set_font("UnicodeFont", size=12)
            break
        except:
            continue
    else:
        raise ValueError("Не найден подходящий Unicode-шрифт")

    pdf.add_page()
    
    # Добавление изображения
    pdf.image(image_path, x=15, y=20, w=180)
    
    # Добавление текста
    safe_text(pdf, "Teplo PP — анализ упаковки")
    safe_text(pdf, "Рекомендации по зоне восприятия")
    
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
        raise HTTPException(500, detail=f"Ошибка: {str(e)}")
        
    finally:
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try: os.remove(f)
                except: pass

@app.get("/")
async def health_check():
    return {"status": "OK"}
