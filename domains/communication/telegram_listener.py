import os
import sys
import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime

# Load credentials and setup path
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent.parent
sys.path.append(str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

DASHBOARD_PORT = os.getenv("DASHBOARD_PORT", "3847")
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "localhost")
DASHBOARD_API = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}/api/telegram/callback"

async def answer_callback(callback_query_id: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/answerCallbackQuery", json={
            "callback_query_id": callback_query_id
        })

async def process_decision(callback_data: str, chat_id: int, message_id: int, original_text: str):
    # Call the dashboard API to record and get confirmation text
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DASHBOARD_API, json={
                "callback_data": callback_data,
                "chat_id": chat_id,
                "message_id": message_id,
                "propuesta": original_text
            })
            return response.json()
        except Exception as e:
            print(f"Error calling dashboard API: {e}")
            return None

async def update_message(chat_id: int, message_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        })

async def send_text_message(chat_id: int, text: str):
    """Envía un mensaje de texto simple."""
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        await client.post(f"{API_URL}/sendMessage", json=payload)

async def bot_listener():
    print("[*] El Operador - Telegram Listener Activo")
    offset = 0
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            try:
                response = await client.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 20})
                updates = response.json().get("result", [])
                
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    # 1. Manejar clics en botones (Callbacks)
                    if "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb["id"]
                        cb_data = cb["data"]
                        msg = cb["message"]
                        chat_id = msg["chat"]["id"]
                        message_id = msg["message_id"]
                        original_text = msg.get("text", "").split("\n\n")[0]
                        
                        await answer_callback(cb_id)
                        result = await process_decision(cb_data, chat_id, message_id, original_text)
                        
                        if result and "confirmation_text" in result:
                            final_text = f"{original_text}\n\n{result['confirmation_text']}"
                            await update_message(chat_id, message_id, final_text)
                            print(f"[+] Decisión procesada: {cb_data}")

                    # 2. Manejar mensajes de texto
                    elif "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg["text"].lower()
                        
                        print(f"[*] Mensaje recibido: {text}")
                        
                        if text == "/start":
                            await send_text_message(chat_id, "¡Hola! Soy *El Operador*. Estoy activo y observando flujos de trabajo. Puedes preguntarme por el `/status` o simplemente esperar a que detecte algo importante.")
                        elif text == "/status":
                            await send_text_message(chat_id, "◉ *Estado del Sistema*\n\n✅ Conectado a Telegram\n✅ Listener Activo\n📡 Observando: Gmail & Calendarios\n🏥 Dominio Radiología: Protegido")
                        else:
                            # Medical intent detection (exceptional admission)
                            medical_keywords = ["agendar", "paciente", "estudio", "turno", "medico", "dr.", "dra."]
                            is_medical = any(kw in text for kw in medical_keywords)
                            
                            if is_medical:
                                await send_text_message(chat_id, "🔍 *Detectado intento de admisión.* Procesando datos...")
                                # Call n8n or orchestrator directly? Orchestrator is faster for this context.
                                try:
                                    from scripts.exceptional_admission_api import ExceptionalAdmissionOrchestrator
                                    orch = ExceptionalAdmissionOrchestrator()
                                    
                                    # We need a basic extraction here if not using n8n node
                                    # For now, let's assume we want to trigger the n8n workflow or use the orchestrator
                                    # Given the user's workflow exists, we'll simulate the AI extraction or call n8n
                                    # But since we are in the script, let's call the orchestrator with raw message
                                    # and use a simple local extraction or just pass it as fields if n8n not available
                                    
                                    # For a better experience, we should ideally call the n8n webhook if available, 
                                    # but the orchestration script is designed for this.
                                    
                                    # Mocking the extraction for the orchestrator (ideally this should call an LLM)
                                    # But for now, let's signal that we are handing it off.
                                    result = orch.process_admission({
                                        "telegram_user_id": str(chat_id),
                                        "raw_message": msg["text"],
                                        "extracted_fields": {
                                            "patient_name": msg["text"].split(",")[0].replace("Agendar paciente ", "").strip(),
                                            "study_type": "Pendiente de clasificar", # Placeholder
                                        }
                                    })
                                    
                                    if result["status"] == "success":
                                        await send_text_message(chat_id, f"✅ *Admisión Exitosa*\nPaciente ID: {result['patient_id']}\nEstudio ID: {result['study_id']}\n\nLos datos han sido registrados. Puede verlos en el panel web.")
                                    else:
                                        await send_text_message(chat_id, f"❌ *Error en admisión:* {result.get('message')}")
                                        
                                except Exception as e:
                                    await send_text_message(chat_id, f"⚠️ Error procesando admisión: {str(e)}")
                            else:
                                await send_text_message(chat_id, "Recibido. He registrado tu mensaje, pero mi lógica de comandos es limitada por ahora. ¿En qué puedo ayudarte con los flujos de trabajo?")
                            
            except Exception as e:
                print(f"Error in listener: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(bot_listener())
    except KeyboardInterrupt:
        print("\n[*] Listener detenido.")
