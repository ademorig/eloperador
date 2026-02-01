import time
import uuid
from datetime import datetime
from core.memory.store_manager import DomainStore

class StudyController:
    def __init__(self):
        self.store = DomainStore("studies.json")

    def create_exceptional_study(self, patient_id, study_type, physician, telegram_user_id, region=""):
        study_id = f"STU-{uuid.uuid4().hex[:8].upper()}"
        
        study_data = {
            "study_id": study_id,
            "patient_id": patient_id,
            "study_type": study_type,
            "region": region,
            "requesting_physician": physician,
            "status": "pending_report",
            "admission_mode": "exceptional_telegram",
            "created_by": telegram_user_id,
            "created_at": datetime.now().isoformat(),
            "exceptional_admission": True
        }
        
        self.store.save_item(study_id, study_data)
        print(f"[Studies] Registered exceptional study {study_type} for patient {patient_id}")
        return study_data

    def get_study(self, study_id: str):
        return self.store.get_by_id(study_id)

    def update_study_status(self, study_id: str, new_status: str):
        study = self.store.get_by_id(study_id)
        if study:
            study["status"] = new_status
            study["updated_at"] = datetime.now().isoformat()
            self.store.save_item(study_id, study)
            return True
        return False

if __name__ == "__main__":
    sc = StudyController()
    s = sc.create_exceptional_study("PAT-ABC123", "TAC de Craneo", "Dr. Gregory", "user_123")
    print(s)
