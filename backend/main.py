from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://teplo-lac.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def generate_report(image_data, output_path):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)
    draw.rectangle([width*0.25, height*0.25, width*0.75, height*0.75], outline="red", width=5)
    temp_image_path = f"{uuid.uuid4().hex}_temp.jpg"
    image.save(temp_image_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Teplo PP - Отчет анализа упаковки", ln=1)
    pdf.image(temp_image_path, x=10, y=30, w=180)
    pdf.ln(100)
    pdf.set_font("Arial", size=12)
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
