from fpdf import FPDF
import os

class PDFReportService:
    def __init__(self, output_dir="outputs/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, report_data: dict) -> str:
        pdf = FPDF()
        pdf.add_page()
        
        # Header - Logo and Title
        logo_path = os.path.join(os.path.dirname(__file__), "..", "templates", "membrete.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=40)
        
        pdf.set_font("helvetica", "B", 18)
        pdf.set_text_color(15, 23, 42) # Dark blue / slate
        pdf.cell(0, 10, "INFORME MÉDICO DE RADIOLOGÍA", ln=True, align="R")
        pdf.ln(2)
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Fecha: {report_data.get('created_at', 'N/A')[:10]} | ID: {report_data.get('study_id', 'N/A')}", ln=True, align="R")
        pdf.ln(15)
        
        # Patient Section Header
        pdf.set_fill_color(241, 245, 249)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, f" PACIENTE: {report_data.get('patient_name', 'N/A').upper()}", ln=True, fill=True)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(100, 8, f" ESTUDIO: {report_data.get('study_type', 'PENDIENTE').upper()}", ln=False)
        pdf.cell(0, 8, f" SOLICITANTE: {report_data.get('requesting_physician', 'NO ESPECIFICADO').upper()}", ln=True, align="R")
        pdf.ln(5)
        
        # Content
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 10, "Hallazgos y Conclusiones:", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, report_data.get("results_summary", ""))
        pdf.ln(25)
        
        # Signature
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 5, f"Firmado por: {report_data.get('physician', 'Dra. IA')}", ln=True, align="R")
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Firma con validez digital - El Operador Radiology Service", ln=True, align="R")
        
        file_path = os.path.join(self.output_dir, f"{report_data['report_id']}.pdf")
        pdf.output(file_path)
        return file_path
