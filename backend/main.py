from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageDraw
import io, os, uuid
from fpdf import FPDF
from pathlib import Path

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена укажите конкретные домены
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "OK", "message": "Сервис анализа упаковки работает"}

def generate_report(image_data, output_path):
    try:
        # Проверка размера изображения (не более 5MB)
        if len(image_data) > 5 * 1024 * 1024:
            raise ValueError("Изображение слишком большое (максимум 5MB)")

        # Проверка и открытие изображения
        try:
            image = Image.open(io.BytesIO(image_data))
            if image.format not in ['JPEG', 'PNG']:
                raise ValueError("Поддерживаются только JPG и PNG изображения")
            image = image.convert("RGB")
        except Exception as e:
            raise ValueError(f"Невозможно обработать изображение: {str(e)}")

        # Отрисовка прямоугольника
        width, height = image.size
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [width*0.25, height*0.25, width*0.75, height*0.75],
            outline="red",
            width=5
        )

        # Сохранение временного файла
        temp_image_path = f"{uuid.uuid4().hex}_temp.jpg"
        image.save(temp_image_path, quality=85)  # Качество 85%

        # Создание PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Шрифт (пробуем оба варианта)
        try:
            font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
            if font_path.exists():
                pdf.add_font("DejaVuSans", "", str(font_path), uni=True)
                pdf.set_font("DejaVuSans", size=14)
            else:
                pdf.set_font("Arial", size=14)
        except:
            pdf.set_font("Arial", size=14)
        
        # Заголовок
        pdf.cell(200, 10, txt="Teplo PP - Анализ упаковки", ln=True)
        
        # Изображение
        pdf.image(temp_image_path, x=10, y=30, w=180)
        
        # Рекомендации
        pdf.set_font(size=12)
        pdf.ln(100)
        pdf.multi_cell(0, 10, txt="Рекомендации:")
        pdf.multi_cell(0, 10, txt="- Центральная зона выделена красным")
        
        pdf.output(output_path)
        os.remove(temp_image_path)

    except Exception as e:
        print(f"[ОШИБКА] При генерации отчета: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании отчета: {str(e)}"
        )

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    # Проверка типа файла
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error": "Поддерживаются только изображения (JPG/PNG)"}
        )

    output_pdf = f"report_{uuid.uuid4().hex}.pdf"
    
    try:
        contents = await file.read()
        generate_report(contents, output_pdf)
        return FileResponse(
            output_pdf,
            media_type="application/pdf",
            filename="teplo_analysis.pdf"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Внутренняя ошибка сервера: {str(e)}"}
        )
    finally:
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
