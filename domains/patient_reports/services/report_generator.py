import uuid
from ..models.report import PatientReport

class ReportGenerator:
    """Service to handle the creation of report contents."""
    
    def generate_report(self, study_id: str, patient_id: str, patient_name: str, study_type: str, results_summary: str, physician: str, requesting_physician: str = "No especificado") -> PatientReport:
        """
        Generates a formal PatientReport object.
        """
        report = PatientReport(
            report_id=f"REP-{uuid.uuid4().hex[:8].upper()}",
            study_id=study_id,
            patient_id=patient_id,
            patient_name=patient_name,
            study_type=study_type,
            results_summary=results_summary,
            physician=physician,
            requesting_physician=requesting_physician,
            status="generated"
        )
        return report

class DeliveryService:
    """Service to manage report delivery through different channels."""
    
    def deliver_report(self, report: PatientReport, channel: str = "telegram") -> bool:
        # In the future, this will call domains/communication
        print(f"[Delivery] Sending report {report.report_id} via {channel} to {report.patient_name}...")
        # Placeholder for actual communication logic
        report.status = "delivered"
        return True
