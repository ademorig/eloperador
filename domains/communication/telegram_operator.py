import os
import json
import httpx
from dotenv import load_dotenv
from pathlib import Path

# Load credentials from the verified .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

async def send_operator_alert(message_text: str, observation_id: str):
    """
    Envía un aviso formateado de El Operador con los 3 botones estándar.
    """
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🤖 Preparar automatización", "callback_data": f"op_prep_{observation_id}"},
            ],
            [
                {"text": "⏭️ Ignorar por ahora", "callback_data": f"op_ignore_{observation_id}"},
                {"text": "⏳ Decidir luego", "callback_data": f"op_later_{observation_id}"}
            ]
        ]
    }
    
    formatted_text = f"◉ *El Operador*\n\n{message_text}\n\n*¿Qué prefieres?*"
    
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": CHAT_ID,
            "text": formatted_text,
            "parse_mode": "Markdown",
            "reply_markup": keyboard
        }
        response = await client.post(f"{API_URL}/sendMessage", json=payload)
        return response.json()

async def send_confirmation(chat_id: str, message_id: int, text: str):
    """
    Edita el mensaje original o envía una confirmación corta.
    """
    async with httpx.AsyncClient() as client:
        # Editamos el mensaje para quitar los botones y mostrar la decisión
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"◉ *El Operador*\n\n{text}\n\n_Entendido. Registrado. Sigo observando._",
            "parse_mode": "Markdown"
        }
        await client.post(f"{API_URL}/editMessageText", json=payload)

if __name__ == "__main__":
    import asyncio
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Enviando mensaje de prueba a Telegram...")
        asyncio.run(send_operator_alert(
            "Prueba de Vida: El sistema de avisos está activo. Detectada conexión con Telegram.",
            "test_id"
        ))
