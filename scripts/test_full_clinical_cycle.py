import sys
import os
import json
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.exceptional_admission_api import ExceptionalAdmissionOrchestrator
from domains.patient_reports.controllers.report_controller import ReportController

def run_test():
    print("🚀 Iniciando prueba de ciclo clínico completo...")
    
    # 1. Simular Admisión Excepcional vía Telegram
    orchestrator = ExceptionalAdmissionOrchestrator()
    admission_input = {
        "telegram_user_id": "TEST_USER_007",
        "raw_message": "Paciente: Carlos Santana, 55 años, M. RX de Pulmón. Dr. Hendrix.",
        "extracted_fields": {
            "patient_name": "Carlos Santana",
            "age": 55,
            "sex": "M",
            "study_type": "RX de Pulmón",
            "physician": "Dr. Hendrix"
        }
    }
    
    print("\n[Paso 1] Realizando Admisión...")
    admission_res = orchestrator.process_admission(admission_input)
    print(json.dumps(admission_res, indent=2))
    
    if admission_res["status"] != "success":
        print("❌ Error en admisión.")
        return

    study_id = admission_res["study_id"]
    
    # 2. Simular Informe Médico
    print(f"\n[Paso 2] Generando Informe para el estudio {study_id}...")
    report_ctrl = ReportController()
    report_res = report_ctrl.process_report(
        study_id=study_id,
        results_summary="Se observa transparencia pulmonar normal. Sin hallazgos patológicos agudos.",
        physician="Dra. Joplin"
    )
    print(json.dumps(report_res, indent=2))
    
    if report_res["status"] == "success":
        print("\n✅ ¡Ciclo clínico completado con éxito!")
        print(f"📊 Reporte ID: {report_res['report_id']}")
    else:
        print("❌ Error en generación de informe.")

if __name__ == "__main__":
    run_test()
