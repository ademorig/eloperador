import time
import uuid
from core.memory.store_manager import DomainStore

class PatientController:
    def __init__(self):
        self.store = DomainStore("patients.json")

    def get_patient_by_id(self, patient_id: str):
        return self.store.get_by_id(patient_id)

    def find_patient(self, name: str, age: int = None):
        """Search for a patient by name and optionally age."""
        all_patients = self.store.get_all()
        for p in all_patients.values():
            # Basic fuzzy match for name and exact for age if provided
            if name.lower() in p["name"].lower():
                if age is None or p.get("age") == age:
                    return p
        return None

    def create_exceptional_patient(self, name: str, age: int, sex: str, telegram_user_id: str):
        """Creates a patient from the telegram admission flow."""
        # Check if exists first
        existing = self.find_patient(name, age)
        if existing:
            print(f"[Patients] Patient already exists: {existing['patient_id']}")
            return existing

        patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        patient_data = {
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "sex": sex,
            "type": "external",
            "source": "telegram",
            "admission_mode": "exceptional_telegram",
            "created_by": telegram_user_id,
            "created_at": datetime.now().isoformat(),
            "exceptional_admission": True
        }
        
        self.store.save_item(patient_id, patient_data)
        print(f"[Patients] Created exceptional patient: {name} ({patient_id})")
        return patient_data

from datetime import datetime
if __name__ == "__main__":
    pc = PatientController()
    p = pc.create_exceptional_patient("Juan Perez", 45, "M", "user_123")
    print(p)
