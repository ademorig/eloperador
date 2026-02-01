import sys
import os
import json
import hashlib
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domains.patients.controllers.patient_controller import PatientController
from domains.studies.controllers.study_controller import StudyController
from core.memory.store_manager import DomainStore

class ExceptionalAdmissionOrchestrator:
    def __init__(self):
        self.patient_ctrl = PatientController()
        self.study_ctrl = StudyController()
        self.audit_store = DomainStore("audit_logs.json")

    def process_admission(self, raw_data: dict):
        """
        Expects raw_data from n8n parsing.
        {
            "telegram_user_id": "...",
            "raw_message": "...",
            "extracted_fields": {
                "patient_name": "...",
                "age": ...,
                "sex": "...",
                "study_type": "...",
                "physician": "..."
            }
        }
        """
        fields = raw_data.get("extracted_fields", {})
        
        # 1. Validation
        required = ["patient_name", "study_type"]
        missing = [f for f in required if not fields.get(f)]
        if missing:
            return {"status": "error", "message": f"Faltan campos críticos: {', '.join(missing)}"}

        # 2. Audit Trail (Hash of raw message)
        msg_hash = hashlib.sha256(raw_data.get("raw_message", "").encode()).hexdigest()
        
        # 3. Domain: Patients
        patient = self.patient_ctrl.create_exceptional_patient(
            name=fields["patient_name"],
            age=fields.get("age"),
            sex=fields.get("sex"),
            telegram_user_id=raw_data["telegram_user_id"]
        )

        # 4. Domain: Studies
        study = self.study_ctrl.create_exceptional_study(
            patient_id=patient["patient_id"],
            study_type=fields["study_type"],
            physician=fields.get("physician", "No especificado"),
            telegram_user_id=raw_data["telegram_user_id"],
            region=fields.get("region", "")
        )

        # 5. Log Audit
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": raw_data["telegram_user_id"],
            "msg_hash": msg_hash,
            "patient_id": patient["patient_id"],
            "study_id": study["study_id"]
        }
        self.audit_store.save_item(f"AUDIT-{int(datetime.now().timestamp())}", audit_entry)

        return {
            "status": "success",
            "patient_id": patient["patient_id"],
            "study_id": study["study_id"],
            "message": "Sistema listo para informar. Admisión completada."
        }

if __name__ == "__main__":
    # Test simulation
    orchestrator = ExceptionalAdmissionOrchestrator()
    sample_input = {
        "telegram_user_id": "999888",
        "raw_message": "Paciente Alberto Rossi, 62 años, masculino. TAC Abdomen. Dr. House.",
        "extracted_fields": {
            "patient_name": "Alberto Rossi",
            "age": 62,
            "sex": "M",
            "study_type": "TAC Abdomen",
            "physician": "Dr. House"
        }
    }
    result = orchestrator.process_admission(sample_input)
    print(json.dumps(result, indent=2))
