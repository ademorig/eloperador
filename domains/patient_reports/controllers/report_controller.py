from ..services.report_generator import ReportGenerator, DeliveryService
from ..services.pdf_service import PDFReportService
from domains.studies.controllers.study_controller import StudyController
from domains.patients.controllers.patient_controller import PatientController
from core.memory.store_manager import DomainStore
import json

class ReportController:
    """Orchestrates the patient report flow, linking studies with results."""
    
    def __init__(self):
        self.generator = ReportGenerator()
        self.delivery = DeliveryService()
        self.pdf_service = PDFReportService()
        self.study_ctrl = StudyController()
        self.patient_ctrl = PatientController()
        self.report_store = DomainStore("reports.json")

    def process_report(self, study_id: str, results_summary: str, physician: str):
        """
        Receives technical results and creates a formal patient report, closing the study.
        """
        print(f"[Reports] Processing report for Study: {study_id}")
        
        # 1. Validate study existence
        study = self.study_ctrl.get_study(study_id)
        if not study:
            return {"status": "error", "message": f"Estudio {study_id} no encontrado."}

        # 2. Get Patient data
        patient = self.patient_ctrl.get_patient_by_id(study["patient_id"])
        patient_name = patient["name"] if patient else "Paciente Desconocido"

        # 3. Generate Report
        report = self.generator.generate_report(
            study_id=study_id,
            patient_id=study["patient_id"],
            patient_name=patient_name,
            study_type=study.get("study_type", "Pendiente"),
            results_summary=results_summary,
            physician=physician,
            requesting_physician=study.get("requesting_physician", "No especificado")
        )
        
        # 3. Persist Report
        report_dict = report.to_dict()
        
        # 4. Generate PDF
        try:
            pdf_path = self.pdf_service.generate_pdf(report_dict)
            report_dict["pdf_path"] = pdf_path
            print(f"[Reports] PDF generado en: {pdf_path}")
        except Exception as e:
            print(f"[Reports] Error generando PDF: {e}")
            
        self.report_store.save_item(report.report_id, report_dict)
        
        # 5. Update Study Status
        self.study_ctrl.update_study_status(study_id, "reported")
        
        # 6. Deliver
        self.delivery.deliver_report(report)
        
        return {
            "status": "success",
            "report_id": report.report_id,
            "study_id": study_id,
            "message": "Informe generado y estudio cerrado correctamente."
        }

if __name__ == "__main__":
    # Test simulation
    controller = ReportController()
    # Assuming STU-XYZ exists or just testing logic
    res = controller.process_report("STU-DEMO123", "Hallazgos compatibles con normalidad.", "Dr. Strange")
    print(json.dumps(res, indent=2))
