import sqlite3
import json
import os
import msvcrt
import contextlib
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "memory.db"

@contextlib.contextmanager
def file_lock(fd):
    """Implementación de bloqueo de archivos para Windows."""
    # Obtener el tamaño actual para bloquear/desbloquear
    fd.seek(0, os.SEEK_END)
    size = fd.tell()
    fd.seek(0)
    
    try:
        # Bloquear desde el inicio (usamos un tamaño grande si está vacío)
        lock_size = max(size, 1)
        msvcrt.locking(fd.fileno(), msvcrt.LK_LOCK, lock_size)
        yield
    finally:
        fd.seek(0)
        msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, lock_size)

def init_db():
    """Inicializa la base de datos SQLite si no existe."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Tabla de decisiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                context TEXT NOT NULL,
                proposal TEXT NOT NULL,
                decision TEXT NOT NULL,
                inferred_reason TEXT,
                learned_pattern TEXT
            )
        ''')
        # Tabla de patrones aprendidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                pattern TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        # Tabla de estadísticas (o simplemente usar queries)
        conn.commit()

def record_decision(
    context: str,
    proposal: str,
    decision: str,
    inferred_reason: Optional[str] = None
) -> Dict[str, Any]:
    """Registra una decisión en la base de datos."""
    timestamp = datetime.now().isoformat()
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO decisions (timestamp, context, proposal, decision, inferred_reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, context, proposal, decision, inferred_reason))
        decision_id = cursor.lastrowid
        conn.commit()
    
    return {
        "id": decision_id,
        "timestamp": timestamp,
        "context": context,
        "proposal": proposal,
        "decision": decision,
        "inferred_reason": inferred_reason
    }

def get_decisions(limit: int = 20) -> List[Dict[str, Any]]:
    """Recupera las últimas decisiones de la base de datos."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_statistics() -> Dict[str, Any]:
    """Calcula estadísticas basadas en las decisiones registradas."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM decisions')
        total = cursor.fetchone()[0]
        
        stats = {"total_proposals": total, "accepted": 0, "rejected": 0, "deferred": 0, "modified": 0}
        
        cursor.execute('SELECT decision, COUNT(*) FROM decisions GROUP BY decision')
        for row in cursor.fetchall():
            decision_type, count = row
            if decision_type == "sí": stats["accepted"] = count
            elif decision_type == "no": stats["rejected"] = count
            elif decision_type == "después": stats["deferred"] = count
            elif decision_type == "modificar": stats["modified"] = count
            
        return stats

def get_learned_patterns() -> List[Dict[str, Any]]:
    """Recupera los patrones aprendidos."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT category, pattern, timestamp FROM learned_patterns')
        return [{"category": r[0], "pattern": r[1], "timestamp": r[2]} for r in cursor.fetchall()]

if __name__ == "__main__":
    init_db()
    print("Base de datos de memoria inicializada.")
    print(f"Estadísticas actuales: {get_statistics()}")
