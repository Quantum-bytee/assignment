import fitz  # PyMuPDF
import pytesseract
from pathlib import Path
from PIL import Image
import io

def extract_text_digital(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def extract_text_scanned(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        page_text = pytesseract.image_to_string(image)
        text += page_text + "\n"
    return text.strip()

def parse_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    text = extract_text_digital(pdf_path)
    if len(text.strip()) < 50:
        # fallback to OCR
        text = extract_text_scanned(pdf_path)
    return text

