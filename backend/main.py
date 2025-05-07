from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Teplo PP API. Используйте /analyze/ для анализа изображений"}

def generate_report(image_data, output_path):
    try:
        # Отладочная информация
        font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
        print(f"Путь к шрифту: {font_path}")
        print(f"Файл существует: {font_path.exists()}")
        
        if not font_path.exists():
            raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")

        # Обработка изображения
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        width, height = image.size
        draw = ImageDraw.Draw(image)
        draw.rectangle([width*0.25, height*0.25, width*0.75, height*0.75], outline="red", width=5)

        temp_image_path = f"{uuid.uuid4().hex}_temp.jpg"
        image.save(temp_image_path)

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVuSans", "", str(font_path), uni=True)
        pdf.set_font("DejaVuSans", size=14)
        pdf.cell(200, 10, txt="Teplo PP — анализ упаковки", ln=True)
        pdf.image(temp_image_path, x=10, y=30, w=180)
        
        pdf.set_font("DejaVuSans", size=12)
        pdf.ln(100)
        pdf.multi_cell(0, 10, txt="Рекомендации:")
        pdf.multi_cell(0, 10, txt="- Упаковка находится вне зоны наблюдения")
        
        pdf.output(output_path)
        os.remove(temp_image_path)
        
    except Exception as e:
        print(f"Ошибка при генерации отчета: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"detail": "Только изображения (JPEG/PNG) поддерживаются"}
        )
    
    output_pdf = f"report_{uuid.uuid4().hex}.pdf"
    try:
        contents = await file.read()
        generate_report(contents, output_pdf)
        return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка обработки: {str(e)}"}
        )
    finally:
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
