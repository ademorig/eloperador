import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde la raíz del proyecto
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuración desde .env
PROJ_DIR = Path(os.getenv("PROJ_DIR", "."))
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
REMOTE_USER = os.getenv("REMOTE_USER")
REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_PORT = os.getenv("REMOTE_PORT", "22")
REMOTE_PATH = os.getenv("REMOTE_PATH")

def validate_config():
    missing = []
    if not SSH_KEY_PATH: missing.append("SSH_KEY_PATH")
    if not REMOTE_USER: missing.append("REMOTE_USER")
    if not REMOTE_HOST: missing.append("REMOTE_HOST")
    if not REMOTE_PATH: missing.append("REMOTE_PATH")
    
    if missing:
        print(f"Error: Faltan variables de entorno requeridas: {', '.join(missing)}")
        print("Por favor configura tu archivo .env basado en .env.example")
        return False
    return True

def run_git(args):
    try:
        result = subprocess.run(["git", "-C", str(PROJ_DIR)] + args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"Error git {' '.join(args)}: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Excepción ejecutando git: {e}")
        return None

def deploy():
    if not validate_config():
        sys.exit(1)

    print(f"[*] Preparando 'El Operador' para el VPS ({REMOTE_HOST})...")
    
    # Init if not already
    if not (PROJ_DIR / ".git").exists():
        run_git(["init"])
    
    # Add files
    run_git(["add", "."])
    
    # Commit
    run_git(["commit", "-m", f"Deploy: Update code {Path(__file__).name}"])
    
    print("\n[!] Código listo en el repositorio local.")
    print("\nComandos sugeridos para enviar al VPS:")
    print("-" * 50)
    
    remote_url = f"ssh://{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}{REMOTE_PATH}"
    print(f"# Configurar remote (si no existe):")
    print(f"git -C {PROJ_DIR} remote remove vps 2> /dev/null || true")
    print(f"git -C {PROJ_DIR} remote add vps {remote_url}")
    print(f"# Enviar código:")
    print(f"git -C {PROJ_DIR} push vps master")
    print("-" * 50)
    print("\nSi el repo no existe en el VPS, primero ejecuta en el servidor:")
    print(f"ssh -p {REMOTE_PORT} {REMOTE_USER}@{REMOTE_HOST} 'mkdir -p {REMOTE_PATH} && cd {REMOTE_PATH} && git init --bare'")

if __name__ == "__main__":
    deploy()
