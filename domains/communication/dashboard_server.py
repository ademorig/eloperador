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

# Paths
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent.parent
load_dotenv(ROOT_DIR / ".env")

DECISION_LOG = ROOT_DIR / "core" / "memory" / "decision_log.json"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Config env
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 3847))

app = FastAPI(
    title="El Operador - Dashboard API",
    description="Read-only dashboard for the persistent agent",
    version="0.3"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Track heartbeat
LAST_HEARTBEAT = datetime.now()


def load_memory() -> dict:
    """Load decision log from disk."""
    if DECISION_LOG.exists():
        with open(DECISION_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "agent": "El Operador",
        "decisions": [],
        "learned_patterns": {},
        "statistics": {"total_proposals": 0, "accepted": 0, "rejected": 0, "deferred": 0, "modified": 0}
    }


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
    memory = load_json(DECISION_LOG, {"statistics": {"total_proposals": 0}})
    obs_log = load_json(OBSERVATIONS_LOG, {"observations": []})
    
    return {
        "agent": "El Operador",
        "version": "v0.3",
        "status": "alive",
        "mode": "Silent Observer",
        "last_heartbeat": LAST_HEARTBEAT.isoformat(),
        "uptime_seconds": (datetime.now() - LAST_HEARTBEAT).total_seconds(),
        "total_decisions": memory["statistics"]["total_proposals"],
        "total_observations": len(obs_log["observations"])
    }

@app.get("/api/observations")
async def get_observations():
    """Get recent observations/proposals."""
    obs_log = load_json(OBSERVATIONS_LOG, {"observations": []})
    decisions = load_json(DECISION_LOG, {"decisions": []}).get("decisions", [])
    
    # Combinar observaciones frescas con decisiones pasadas
    recent = obs_log["observations"] + decisions[-10:]
    
    return {
        "count": len(obs_log["observations"]),
        "recent": list(reversed(recent))[:20],
        "summary": {
            "today": len(obs_log["observations"]),
            "accumulated": len(decisions)
        }
    }


@app.get("/api/runs")
async def get_runs():
    """Get flow execution history (simulated for now, will integrate with n8n)."""
    # TODO: Integrate with n8n API to get actual workflow runs
    memory = load_memory()
    
    return {
        "total_runs": memory["statistics"]["total_proposals"],
        "successful": memory["statistics"]["accepted"],
        "failed": 0,
        "pending": memory["statistics"]["deferred"],
        "last_run": memory["decisions"][-1]["timestamp"] if memory["decisions"] else None,
        "history": [
            {
                "id": i,
                "timestamp": d.get("timestamp"),
                "type": "observation",
                "status": "completed" if d.get("decision_usuario") in ["sí", "no"] else "pending",
                "context": d.get("contexto", "")[:50]
            }
            for i, d in enumerate(reversed(memory.get("decisions", [])[-10:]))
        ]
    }


@app.get("/api/memory")
async def get_memory():
    """Get accumulated memory and learned patterns."""
    memory = load_memory()
    
    return {
        "version": memory.get("version", "1.0"),
        "created": memory.get("created"),
        "statistics": memory.get("statistics", {}),
        "learned_patterns": memory.get("learned_patterns", {}),
        "total_entries": len(memory.get("decisions", [])),
        "acceptance_rate": (
            round(memory["statistics"]["accepted"] / memory["statistics"]["total_proposals"] * 100, 1)
            if memory["statistics"]["total_proposals"] > 0 else 0
        )
    }


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
    action = parts[1] # prep, ignore, later
    obs_id = parts[2]
    
    # Mapear accion a decision y mensaje de consecuencia
    messages = {
        "prep": {
            "decision": "sí",
            "text": "Decisión registrada: Preparar automatización.",
            "consequence": "Se generará un flujo de borrador basado en este patrón para tu revisión."
        },
        "ignore": {
            "decision": "no",
            "text": "Decisión registrada: Ignorar por ahora.",
            "consequence": "Este patrón se seguirá observando en silencio sin nuevas notificaciones."
        },
        "later": {
            "decision": "después",
            "text": "Decisión registrada: Decidir luego.",
            "consequence": "Este aviso se ha guardado en memoria para revisión futura. El ciclo actual finaliza."
        }
    }
    
    mapping = messages.get(action, messages["later"])
    
    # Registrar en memoria
    # Usamos import dinámico para evitar problemas de circularidad o paths en desarrollo
    import sys
    sys.path.append(str(ROOT_DIR / "core" / "memory"))
    from memory_manager import record_decision
    record_decision(
        contexto=f"Telegram Alert {obs_id}",
        propuesta=data.get("propuesta", "Acción vía Telegram"),
        decision=mapping["decision"],
        razon_inferida=f"Respuesta directa vía Telegram: {mapping['text']}"
    )
    
    return {
        "status": "recorded",
        "action": action,
        "confirmation_text": f"*{mapping['text']}*\n_{mapping['consequence']}_"
    }


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
    uvicorn.run(app, host=DASHBOARD_HOST, port=DASHBOARD_PORT)
