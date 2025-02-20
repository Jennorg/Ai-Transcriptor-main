from fpdf import FPDF

def save_as_pdf(file_path, title, content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='', size=12)
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, content)
    pdf.output(file_path)

def save_as_txt(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
