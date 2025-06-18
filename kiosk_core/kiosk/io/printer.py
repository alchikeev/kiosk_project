import subprocess
import os
import shutil
from datetime import datetime

# Расширения для конвертации
CONVERTIBLE_EXTENSIONS = {'.docx', '.odt', '.pptx', '.jpg', '.jpeg', '.png', '.doc', '.xls', '.xlsx', '.ppt', '.odp', '.ods'}
DIRECT_PRINT_EXTENSIONS = {'.pdf', '.txt'}

# Папка для временных PDF
STATIC_TMP_DIR = "/tmp/kiosk_prints"
os.makedirs(STATIC_TMP_DIR, exist_ok=True)

def print_file(file_path, pages=None):
    """
    Печатает файл. Если передан список страниц (pages), то печатает только их.
    Поддержка диапазона работает только для PDF.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext in CONVERTIBLE_EXTENSIONS:
            print(f"ℹ Конвертация {ext} → PDF...")
            filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_pdf = os.path.join(STATIC_TMP_DIR, f"{filename_no_ext}_{timestamp}.pdf")

            result = subprocess.run([
                "libreoffice", "--headless", "--convert-to", "pdf", file_path, "--outdir", STATIC_TMP_DIR
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"❌ Ошибка при конвертации: {result.stderr}")
                raise RuntimeError("Ошибка при конвертации в PDF")

            candidate_pdf = os.path.join(STATIC_TMP_DIR, f"{filename_no_ext}.pdf")
            if os.path.exists(candidate_pdf):
                shutil.move(candidate_pdf, output_pdf)

            if not os.path.exists(output_pdf):
                raise FileNotFoundError("PDF не найден после конвертации")

            print(f"✅ Успешно конвертировано: {output_pdf}")
            file_path = output_pdf
            ext = ".pdf"

        elif ext in {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}:
            from PIL import Image
            print(f"ℹ Конвертация изображения {ext} → PDF...")
            image = Image.open(file_path)
            rgb_image = image.convert('RGB')

            filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_pdf = os.path.join(STATIC_TMP_DIR, f"{filename_no_ext}_{timestamp}.pdf")
            rgb_image.save(output_pdf, "PDF")
            file_path = output_pdf
            ext = ".pdf"

        elif ext not in DIRECT_PRINT_EXTENSIONS:
            raise ValueError(f"Формат {ext} не поддерживается")

        # Печать
        if pages and ext == ".pdf":
            page_range = ",".join(str(p) for p in pages)
            print(f"📄 Печать выбранных страниц: {page_range}")
            subprocess.run(["lp", "-o", f"page-ranges={page_range}", file_path], check=True)
        else:
            subprocess.run(["lp", file_path], check=True)

        print(f"✅ Отправлен на печать: {file_path}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при печати: {e}")
        raise
    except Exception as e:
        print(f"❌ Общая ошибка при обработке файла: {e}")
        raise
