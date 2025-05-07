from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена замените на конкретные домены
    allow_methods=["POST"],
    allow_headers=["*"],
)

def generate_report(image_data, output_path):
    try:
        # Обработка изображения
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        width, height = image.size
        draw = ImageDraw.Draw(image)
        draw.rectangle([width*0.25, height*0.25, width*0.75, height*0.75], outline="red", width=5)

        # Временный файл изображения
        temp_image_path = f"{uuid.uuid4().hex}_temp.jpg"
        image.save(temp_image_path)

        # Путь к шрифту (относительно расположения main.py)
        font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
        
        # Проверка наличия шрифта
        if not font_path.exists():
            raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")

        # Создание PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Добавляем шрифт
        pdf.add_font("DejaVuSans", "", str(font_path), uni=True)
        pdf.set_font("DejaVuSans", size=14)
        
        # Заголовок с Unicode
        pdf.cell(200, 10, txt="Teplo PP — анализ упаковки", ln=True)
        pdf.image(temp_image_path, x=10, y=30, w=180)
        
        # Текст рекомендаций
        pdf.set_font("DejaVuSans", size=12)
        pdf.ln(100)
        pdf.multi_cell(0, 10, txt="Рекомендации:")
        pdf.multi_cell(0, 10, txt="- Упаковка находится вне зоны наблюдения")
        pdf.multi_cell(0, 10, txt="- Используйте яркие цвета ближе к центру")
        
        pdf.output(output_path)
        os.remove(temp_image_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Только изображения (JPEG/PNG) поддерживаются")
    
    output_pdf = f"report_{uuid.uuid4().hex}.pdf"
    try:
        contents = await file.read()
        generate_report(contents, output_pdf)
        return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf)
    finally:
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
