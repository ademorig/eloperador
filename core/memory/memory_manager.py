from datetime import datetime
import json
import os
import time
from pathlib import Path
from typing import Literal, Optional
import contextlib

# Intentar importar fcntl para bloqueo en Linux/Mac
try:
    import fcntl
except ImportError:
    fcntl = None

# Intentar importar msvcrt para bloqueo en Windows
try:
    import msvcrt
except ImportError:
    msvcrt = None

DECISION_LOG_PATH = Path(__file__).parent / "decision_log.json"

DecisionType = Literal["sí", "no", "después", "modificar"]

@contextlib.contextmanager
def file_lock(file_handle):
    """Gestor de contexto para bloqueo de archivos multiplataforma robusto."""
    if fcntl:
        # Linux/Unix/Mac: Bloqueo bloqueante (espera hasta adquirir)
        fcntl.flock(file_handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(file_handle, fcntl.LOCK_UN)
    elif msvcrt:
        # Windows: Implementación con reintentos
        # msvcrt.locking lanza IOError si no puede bloquear inmediatamente
        max_retries = 10
        delay = 0.05
        locked = False
        pos = file_handle.tell()
        
        for _ in range(max_retries):
            try:
                file_handle.seek(0)
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1) # LK_NBLCK no bloquea, lanza error
                locked = True
                break
            except (IOError, OSError):
                time.sleep(delay)
        
        if not locked:
             # Si falla tras reintentos, esperamos una vez más con bloqueo (si es soportado) o lanzamos error
             # Pero para evitar crash, intentamos seguir (unsafe) o lanzamos. 
             # Mejor lanzar para evitar corrupción.
             raise OSError("No se pudo adquirir el bloqueo del archivo de memoria en Windows.")

        try:
            yield
        finally:
            file_handle.seek(0)
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
            file_handle.seek(pos)
    else:
        # Fallback sin bloqueo (warn user usually)
        yield

def load_memory() -> dict:
    """Carga el estado actual de la memoria."""
    if DECISION_LOG_PATH.exists():
        try:
            with open(DECISION_LOG_PATH, "r", encoding="utf-8") as f:
                # Opcional: Bloqueo compartido para lectura (fcntl.LOCK_SH)
                # Por simplicidad y rendimiento lectura sin lock suele ser aceptable si la escritura es atómica
                # Pero con 'w' truncate, existe riesgo de leer vacío.
                # Mejor usar bloqueo compartido si fcntl está disponible.
                if fcntl:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    try:
                        return json.load(f)
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)
                else:
                     return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass 
    return {
        "version": "1.0",
        "agent": "El Operador",
        "created": datetime.now().isoformat(),
        "decisions": [],
        "learned_patterns": {
            "email_preferences": [],
            "calendar_preferences": [],
            "automation_style": None,
            "communication_frequency": "default"
        },
        "statistics": {
            "total_proposals": 0,
            "accepted": 0,
            "rejected": 0,
            "deferred": 0,
            "modified": 0
        }
    }


def save_memory(memory: dict) -> None:
    """Persiste la memoria a disco con bloqueo para evitar corrupción."""
    # Estrategia: "a+" permite leer/escribir.
    with open(DECISION_LOG_PATH, "a+", encoding="utf-8") as f:
        with file_lock(f):
            f.seek(0)
            f.truncate()
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())


def record_decision(
    contexto: str,
    propuesta: str,
    decision: DecisionType,
    razon_inferida: Optional[str] = None
) -> dict:
    """Registra una decisión del usuario y actualiza estadísticas."""
    memory = load_memory()
    
    registro = {
        "timestamp": datetime.now().isoformat(),
        "contexto": contexto,
        "propuesta": propuesta,
        "decision_usuario": decision,
        "razon_inferida": razon_inferida,
        "patrón_aprendido": None
    }
    
    memory["statistics"]["total_proposals"] += 1
    
    if decision == "sí":
        memory["statistics"]["accepted"] += 1
    elif decision == "no":
        memory["statistics"]["rejected"] += 1
    elif decision == "después":
        memory["statistics"]["deferred"] += 1
    elif decision == "modificar":
        memory["statistics"]["modified"] += 1
    
    pattern = detect_pattern(memory["decisions"], propuesta, decision)
    if pattern:
        registro["patrón_aprendido"] = pattern
        memory["learned_patterns"]["email_preferences"].append(pattern)
    
    memory["decisions"].append(registro)
    
    if len(memory["decisions"]) > 100:
        memory["decisions"] = memory["decisions"][-100:]
    
    save_memory(memory)
    return registro


def detect_pattern(decisions: list, propuesta: str, decision: DecisionType) -> Optional[str]:
    keywords = set(propuesta.lower().split())
    
    similar_decisions = []
    for d in decisions[-20:]:
        d_keywords = set(d["propuesta"].lower().split())
        overlap = len(keywords & d_keywords) / max(len(keywords), 1)
        if overlap > 0.5:
            similar_decisions.append(d["decision_usuario"])
    
    if len(similar_decisions) >= 2:
        if all(d == decision for d in similar_decisions[-2:]):
            if decision == "no":
                return f"Usuario rechaza consistentemente: {propuesta[:50]}..."
            elif decision == "sí":
                return f"Usuario acepta rápidamente: {propuesta[:50]}..."
    
    return None


def get_statistics() -> dict:
    return load_memory()["statistics"]


def get_learned_patterns() -> list:
    return load_memory()["learned_patterns"]


def should_propose(propuesta_tipo: str) -> bool:
    memory = load_memory()
    rejections = 0
    for d in memory["decisions"][-30:]:
        if propuesta_tipo.lower() in d["propuesta"].lower():
            if d["decision_usuario"] == "no":
                rejections += 1
    return rejections < 3


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python memory_manager.py stats     - Ver estadísticas")
        print("  python memory_manager.py patterns  - Ver patrones aprendidos")
        print("  python memory_manager.py record    - Registrar decisión")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "stats":
        stats = get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif cmd == "patterns":
        patterns = get_learned_patterns()
        print(json.dumps(patterns, indent=2, ensure_ascii=False))
    
    elif cmd == "record":
        print("Modo interactivo no disponible en este entorno, use argumentos o importe el módulo.")
