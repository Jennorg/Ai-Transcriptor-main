from fpdf import FPDF
import os
from datetime import datetime

def save_as_pdf(transcription_text, filename=None):
    """Guarda la transcripción como archivo PDF."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcripcion_{timestamp}.pdf"
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Dividir el texto en líneas que quepan en la página
    lines = transcription_text.split('\n')
    for line in lines:
        pdf.cell(200, 10, txt=line, ln=1, align="L")
    
    pdf.output(filename)
    return filename

def save_as_txt(transcription_text, filename=None):
    """Guarda la transcripción como archivo de texto."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcripcion_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(transcription_text)
    
    return filename
