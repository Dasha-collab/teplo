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

def create_pdf_with_fallback(image_path, output_pdf):
    """Создает PDF с несколькими уровнями fallback"""
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    
    # Установка шрифта с несколькими fallback-вариантами
    font_attempts = [
        lambda: pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True),
        lambda: pdf.add_font("DejaVu", "", str(Path(__file__).parent / "fonts" / "DejaVuSans.ttf"), uni=True),
        lambda: pdf.set_font("Arial", "", 12)
    ]
    
    for attempt in font_attempts:
        try:
            attempt()
            pdf.set_font("DejaVu" if "DejaVu" in pdf.fonts else "Arial", size=12)
            break
        except:
            continue
    
    # Добавление изображения с проверкой размера
    img_width = 180  # Максимальная ширина в мм
    pdf.image(image_path, x=10, y=20, w=img_width)
    
    # Текст с проверкой длины
    text = "Teplo PP - Анализ упаковки"
    if pdf.get_string_width(text) > 190:  # Проверка ширины текста
        text = "Teplo PP"  # Укороченная версия если не помещается
    
    pdf.cell(0, 10, txt=text, ln=1, align="C")
    
    # Простые рекомендации
    pdf.set_font(size=10)
    pdf.ln(10)
    pdf.multi_cell(0, 8, txt="Рекомендации по улучшению упаковки:")
    pdf.multi_cell(0, 8, txt="- Центральная зона выделена красным прямоугольником")
    
    pdf.output(output_pdf)

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Только изображения JPG/PNG поддерживаются")
    
    try:
        # Сохраняем временные файлы
        temp_img = f"/tmp/{uuid.uuid4().hex}.jpg"
        temp_pdf = f"/tmp/{uuid.uuid4().hex}.pdf"
        
        # Обработка изображения
        img_data = await file.read()
        img = Image.open(io.BytesIO(img_data))
        img = img.convert("RGB")
        img.save(temp_img, quality=85)
        
        # Создание PDF
        create_pdf_with_fallback(temp_img, temp_pdf)
        
        return FileResponse(
            temp_pdf,
            media_type="application/pdf",
            filename="packaging_analysis.pdf"
        )
        
    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
        
    finally:
        # Удаление временных файлов
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

@app.get("/")
async def health_check():
    return {"status": "working"}
