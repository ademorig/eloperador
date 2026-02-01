import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print(f"TELEGRAM_TOKEN: {token}")
print(f"TELEGRAM_CHAT_ID: {chat_id}")

if not token or not chat_id:
    print("\n[!] ERROR: Faltan las credenciales de Telegram en el archivo .env")
else:
    print("\n[+] Credenciales encontradas. Intentando envío...")
    import asyncio
    import httpx
    
    async def test():
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": "Test de conexión desde El Operador"}
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url, json=payload)
                print(f"Status Code: {r.status_code}")
                print(f"Response: {r.text}")
            except Exception as e:
                print(f"Error: {e}")

    asyncio.run(test())
