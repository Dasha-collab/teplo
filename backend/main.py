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
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "working", "message": "Teplo PP Analysis Service"}

def generate_report(image_data, output_path):
    try:
        # Проверка и загрузка изображения
        image = Image.open(io.BytesIO(image_data))
        if image.format not in ['JPEG', 'PNG']:
            raise ValueError("Only JPEG/PNG images supported")
        
        # Конвертация в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Создание временного файла изображения
        temp_img_path = f"/tmp/{uuid.uuid4().hex}.jpg"
        image.save(temp_img_path, quality=85)
        
        # Инициализация PDF
        pdf = FPDF(unit="mm", format="A4")
        pdf.add_page()
        
        # Настройка шрифта (пробуем несколько вариантов)
        try:
            font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
            if font_path.exists():
                pdf.add_font("DejaVu", "", str(font_path), uni=True)
                pdf.set_font("DejaVu", size=12)
            else:
                pdf.set_font("Arial", size=12)
        except:
            pdf.set_font("Helvetica", size=12)
        
        # Добавление заголовка
        pdf.cell(200, 10, txt="Teplo PP - Packaging Analysis", ln=1, align='C')
        
        # Добавление изображения (макс. ширина 180mm)
        pdf.image(temp_img_path, x=10, y=30, w=180)
        
        # Добавление рекомендаций
        pdf.set_font(size=10)
        pdf.ln(120)
        pdf.multi_cell(0, 8, txt="Recommendations:")
        pdf.multi_cell(0, 8, txt="- Product is outside the focus area")
        
        # Сохранение PDF
        pdf.output(output_path)
        os.remove(temp_img_path)
        
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")
    
    output_pdf = f"/tmp/report_{uuid.uuid4().hex}.pdf"
    
    try:
        contents = await file.read()
        generate_report(contents, output_pdf)
        return FileResponse(output_pdf, media_type="application/pdf", filename="packaging_analysis.pdf")
    finally:
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
