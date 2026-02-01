#!/usr/bin/env python
"""
El Operador - Dashboard API Server
Serves the read-only dashboard and provides status endpoints.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from dotenv import load_dotenv

import sys
from pathlib import Path
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent.parent
load_dotenv(ROOT_DIR / ".env")

sys.path.append(str(ROOT_DIR / "core" / "memory"))
import memory_manager

DECISION_LOG = ROOT_DIR / "core" / "memory" / "decision_log.json"
DASHBOARD_DIR = ROOT_DIR / "domains" / "dashboard" # Using the professional UI

# Clinical imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from domains.patients.controllers.patient_controller import PatientController
from domains.studies.controllers.study_controller import StudyController
from domains.patient_reports.controllers.report_controller import ReportController
from core.memory.store_manager import DomainStore
from pydantic import BaseModel

# Controllers
patient_ctrl = PatientController()
study_ctrl = StudyController()
report_ctrl = ReportController()

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'reports'))
os.makedirs(REPORTS_DIR, exist_ok=True)

# Config env
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 3847))

app = FastAPI(
    title="El Operador - Unified Dashboard",
    description="Unified clinical and agent dashboard",
    version="0.5"
)

app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

class ReportDraft(BaseModel):
    study_id: str
    results_summary: str
    physician: str

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Track heartbeat
LAST_HEARTBEAT = datetime.now()


# Removed load_memory in favor of memory_manager direct calls


OBSERVATIONS_LOG = BASE_DIR / "observations_log.json"

def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

@app.post("/api/observations")
async def post_observation(observation: dict):
    """Endpoint para que n8n envíe observaciones en tiempo real."""
    global LAST_HEARTBEAT
    LAST_HEARTBEAT = datetime.now()
    
    logs = load_json(OBSERVATIONS_LOG, {"observations": []})
    observation["timestamp"] = datetime.now().isoformat()
    logs["observations"].append(observation)
    
    # Mantener solo las últimas 50
    logs["observations"] = logs["observations"][-50:]
    
    with open(OBSERVATIONS_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
        
    return {"status": "recorded", "timestamp": observation["timestamp"]}

@app.get("/api/status")
async def get_status():
    """Get agent status and heartbeat."""
    global LAST_HEARTBEAT
    stats = memory_manager.get_statistics()
    obs_log = load_json(OBSERVATIONS_LOG, {"observations": []})
    
    return {
        "agent": "El Operador",
        "version": "v0.3",
        "status": "alive",
        "mode": "Silent Observer",
        "last_heartbeat": LAST_HEARTBEAT.isoformat(),
        "uptime_seconds": (datetime.now() - LAST_HEARTBEAT).total_seconds(),
        "total_decisions": stats["total_proposals"],
        "total_observations": len(obs_log["observations"])
    }

@app.get("/api/observations")
async def get_observations():
    """Get recent observations/proposals."""
    obs_log = load_json(OBSERVATIONS_LOG, {"observations": []})
    decisions = memory_manager.get_decisions(limit=10)
    
    # Combinar observaciones frescas con decisiones pasadas
    recent = obs_log["observations"] + decisions
    
    return {
        "count": len(obs_log["observations"]),
        "recent": sorted(recent, key=lambda x: x.get('timestamp', ''), reverse=True)[:20],
        "summary": {
            "today": len(obs_log["observations"]),
            "accumulated": memory_manager.get_statistics()["total_proposals"]
        }
    }


@app.get("/api/runs")
async def get_runs():
    """Get flow execution history (simulated for now, will integrate with n8n)."""
    # TODO: Integrate with n8n API to get actual workflow runs
    stats = memory_manager.get_statistics()
    decisions = memory_manager.get_decisions(limit=10)
    
    return {
        "total_runs": stats["total_proposals"],
        "successful": stats["accepted"],
        "failed": 0,
        "pending": stats["deferred"],
        "last_run": decisions[0]["timestamp"] if decisions else None,
        "history": [
            {
                "id": d.get("id"),
                "timestamp": d.get("timestamp"),
                "type": "observation",
                "status": "completed" if d.get("decision") in ["sí", "no"] else "pending",
                "context": d.get("context", "")[:50]
            }
            for d in decisions
        ]
    }


@app.get("/api/memory")
async def get_memory():
    """Get accumulated memory and learned patterns."""
    stats = memory_manager.get_statistics()
    patterns = memory_manager.get_learned_patterns()
    decisions = memory_manager.get_decisions(limit=1)
    
    return {
        "version": "2.0",
        "statistics": stats,
        "learned_patterns": patterns,
        "total_entries": stats["total_proposals"],
        "acceptance_rate": (
            round(stats["accepted"] / stats["total_proposals"] * 100, 1)
            if stats["total_proposals"] > 0 else 0
        )
    }


@app.post("/api/observations/decide")
async def decide_observation(data: dict):
    """
    Endpoint para tomar decisiones desde el Dashboard.
    """
    obs_id = data.get("id")
    action = data.get("action") # sí, no, después
    proposal = data.get("proposal", "Acción vía Dashboard")
    
    # Registrar en memoria SQLite
    result = memory_manager.record_decision(
        contexto=f"Dashboard Decisión {obs_id}",
        propuesta=proposal,
        decision=action,
        razon_inferida="Decisión manual desde Dashboard"
    )
    
    # Eliminar de observaciones pendientes si aplica
    logs = load_json(OBSERVATIONS_LOG, {"observations": []})
    logs["observations"] = [o for o in logs["observations"] if o.get("id") != obs_id]
    
    with open(OBSERVATIONS_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
        
    return {"status": "recorded", "decision": action, "id": result["id"]}

@app.post("/api/telegram/callback")
async def telegram_callback(data: dict):
    """
    Maneja las pulsaciones de botones de Telegram.
    Formato callback_data: op_[accion]_[id]
    """
    callback_data = data.get("callback_data", "")
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")
    
    if not callback_data.startswith("op_"):
        return {"status": "ignored"}
    
    parts = callback_data.split("_")
    action = parts[1] # prep (sí), ignore (no), later (después)
    obs_id = parts[2]
    
    # Mapear accion a decision y mensaje de consecuencia
    mapping = {
        "prep": {"decision": "sí", "text": "Preparar automatización"},
        "ignore": {"decision": "no", "text": "Ignorar"},
        "later": {"decision": "después", "text": "Decidir luego"}
    }.get(action, {"decision": "después", "text": "Decidir luego"})
    
    # Registrar en memoria SQLite
    memory_manager.record_decision(
        contexto=f"Telegram Alert {obs_id}",
        propuesta=data.get("propuesta", "Acción vía Telegram"),
        decision=mapping["decision"],
        razon_inferida=f"Respuesta directa vía Telegram: {mapping['text']}"
    )
    
    return {
        "status": "recorded",
        "action": action,
        "confirmation_text": f"*Decisión registrada: {mapping['text']}*"
    }

# --- Clinical Endpoints ---

@app.get("/api/data")
async def get_all_data():
    patients = DomainStore("patients.json").get_all()
    studies = DomainStore("studies.json").get_all()
    reports = DomainStore("reports.json").get_all()
    
    return {
        "patients": list(patients.values()),
        "studies": list(studies.values()),
        "reports": list(reports.values())
    }

@app.post("/api/reports")
async def create_report(draft: ReportDraft):
    result = report_ctrl.process_report(
        study_id=draft.study_id,
        results_summary=draft.results_summary,
        physician=draft.physician
    )
    if result["status"] == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


from scripts.exceptional_admission_api import ExceptionalAdmissionOrchestrator

@app.post("/api/admission")
async def dashboard_admission(data: dict):
    """
    Endpoint para registrar un nuevo estudio desde el Dashboard.
    """
    orchestrator = ExceptionalAdmissionOrchestrator()
    
    # Formatear datos para el orquestador similar a n8n
    admission_data = {
        "telegram_user_id": "DASHBOARD",
        "raw_message": f"Admisión manual Dashboard: {data.get('patient_name')}",
        "extracted_fields": {
            "patient_name": data.get("patient_name"),
            "study_type": data.get("study_type"),
            "physician": data.get("physician"),
            "region": data.get("region", "")
        }
    }
    
    result = orchestrator.process_admission(admission_data)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard."""
    dashboard_file = DASHBOARD_DIR / "index.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    
    # Fallback inline dashboard
    return """
    <!DOCTYPE html>
    <html><head><title>El Operador - Dashboard</title></head>
    <body style="background:#0a0e1a;color:#e2e8f0;font-family:monospace;padding:40px;text-align:center;">
        <h1>⚙️ El Operador</h1>
        <p>Dashboard loading... Check /api/status</p>
    </body></html>
    """


# Mount static files if dashboard folder exists
if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")


if __name__ == "__main__":
    print("[*] El Operador - Dashboard Server")
    print(f"    http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print("    Endpoints: /api/status, /api/observations, /api/runs, /api/memory")
    uvicorn.run(app, host=DASHBOARD_HOST, port=DASHBOARD_PORT, reload=True)
