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

def generate_pdf(image_path, output_pdf):
    pdf = FPDF(unit="mm", format="A4")
    
    # Шрифты с приоритетом: Noto Sans → DejaVu → Arial Unicode
    try:
        font_path = Path(__file__).parent / "fonts" / "NotoSans-Regular.ttf"
        if font_path.exists():
            pdf.add_font("NotoSans", "", str(font_path), uni=True)
            pdf.set_font("NotoSans", size=12)
        else:
            raise FileNotFoundError
    except Exception as e:
        logger.warning(f"Noto Sans not found, trying DejaVu: {e}")
        try:
            font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
            pdf.add_font("DejaVu", "", str(font_path), uni=True)
            pdf.set_font("DejaVu", size=12)
        except Exception as e:
            logger.warning(f"DejaVu not found, using Arial: {e}")
            pdf.set_font("Arial", size=12)
    
    pdf.add_page()
    
    # Добавление изображения (макс. ширина 180mm с центрированием)
    img_width = 180
    pdf.image(image_path, x=(210-img_width)/2, y=20, w=img_width)
    
    # Текст отчета
    pdf.set_y(100)
    pdf.cell(0, 10, "Teplo PP - Анализ упаковки", 0, 1, 'C')
    pdf.ln(5)
    pdf.multi_cell(0, 8, "Рекомендации по зоне восприятия:\n• Оптимальное размещение\n• Цветовые решения\n• Размеры элементов", 0, 'L')
    
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
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=f"Ошибка обработки: {str(e)}")
    finally:
        for f in [temp_img, temp_pdf]:
            if f and os.path.exists(f):
                try: os.remove(f)
                except: pass

@app.get("/")
async def health_check():
    return {"status": "OK", "version": "1.0.0"}
