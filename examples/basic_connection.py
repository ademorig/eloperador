"""
Ejemplo básico: Conexión simple al servidor MCP de n8n.

Este script demuestra cómo establecer una conexión básica y verificar
que el servidor está respondiendo correctamente.
"""

import asyncio
import httpx
import sys
import os
import io
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv

# Fix Windows UTF-8 encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


async def main():
    """Conexión básica al servidor MCP."""
    
    url = os.getenv('N8N_MCP_URL')
    token = os.getenv('N8N_API_TOKEN')
    
    if not url or not token:
        print("❌ Error: Configura N8N_MCP_URL y N8N_API_TOKEN en .env")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(headers=headers, timeout=None) as http_client:
        async with streamable_http_client(url, http_client=http_client) as (read, write, close):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Conexión exitosa al servidor MCP de n8n")
                print(f"📍 URL: {url}")
                
                # Listar herramientas disponibles
                tools = await session.list_tools()
                print(f"\n🧰 Herramientas disponibles: {len(tools.tools)}")
                
                for tool in tools.tools:
                    print(f"\n  📌 {tool.name}")
                    print(f"     {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
