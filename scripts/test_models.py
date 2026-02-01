from domains.patients.models.patient import Patient
from domains.studies.models.study import Study
from datetime import date

def test_models():
    try:
        p = Patient(
            ID=1,
            CENTER_CODE="CENTRAL",
            MRN="12345",
            NAME="John",
            LASTNAME="Doe",
            SEX="M",
            BIRTH_DATE=date(1990, 1, 1),
            EMAIL="john@example.com"
        )
        print(f"Patient model OK: {p.name} {p.lastname}")

        s = Study(
            ID=101,
            REQUEST_NO="REQ-001",
            ACCESSION="ACC-2024-001",
            XRAY_CODE="B0101",
            STATUS="NEW",
            URGENT=True
        )
        print(f"Study model OK: {s.accession} - {s.status}")
    except Exception as e:
        print(f"Error validating models: {e}")

if __name__ == "__main__":
    test_models()
