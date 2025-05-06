from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://teplo-lac.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Новый корневой маршрут:
@app.get("/")
async def root():
    return {"message": "Сервер работает. Используйте POST /analyze/ для анализа изображений."}

# Остальной ваш код (generate_report, /analyze/) без изменений:
# ...
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

def generate_report(image_data, output_path):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)
    draw.rectangle([width*0.25, height*0.25, width*0.75, height*0.75], outline="red", width=5)

    temp_image_path = f"{uuid.uuid4().hex}_temp.jpg"
    image.save(temp_image_path)

    pdf = FPDF()
    pdf.add_page()

    # Загрузка шрифта с поддержкой кириллицы
    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=14)
    pdf.cell(200, 10, txt="Teplo PP — Отчет анализа упаковки", new_x=XPos.LEFT, new_y=YPos.NEXT)

    pdf.image(temp_image_path, x=10, y=30, w=180)

    pdf.set_font("DejaVu", size=12)
    pdf.ln(100)
    pdf.multi_cell(0, 10, txt="Рекомендации:")
    pdf.multi_cell(0, 10, txt="- Упаковка находится вне зоны наблюдения: задняя крышка ближе к центру.")
    pdf.multi_cell(0, 10, txt="- Повышайте контрастность между текстом и фоном.")
    pdf.multi_cell(0, 10, txt="- Используйте яркие цвета ближе к центру упаковки.")
    pdf.multi_cell(0, 10, txt="- Добавьте акцентные элементы (иконки, метки) в правую часть.")

    pdf.output(output_path)
    os.remove(temp_image_path)


@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    output_pdf = f"report_{uuid.uuid4().hex}.pdf"
    generate_report(contents, output_pdf)
    return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf)
