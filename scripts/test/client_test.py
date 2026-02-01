import asyncio
import httpx
import sys
import os
import io
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv

# Fix Windows UTF-8 encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

async def main():
    """
    Script de prueba para verificar la conexión con el servidor MCP de n8n.
    Muestra las herramientas disponibles y ejecuta una búsqueda de workflows.
    """
    
    # Get credentials from environment
    url = os.getenv('N8N_MCP_URL')
    token = os.getenv('N8N_API_TOKEN')
    
    if not url or not token:
        print("❌ Error: N8N_MCP_URL y N8N_API_TOKEN deben estar definidos en .env")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        async with httpx.AsyncClient(
            headers=headers,
            timeout=None  # Sin timeout para streaming
        ) as http_client:

            async with streamable_http_client(
                url,
                http_client=http_client,
            ) as (read, write, close):

                async with ClientSession(read, write) as session:
                    await session.initialize()

                    print("\n✅ [OK] Conectado al MCP de n8n\n")

                    # Listar herramientas disponibles
                    tools = await session.list_tools()
                    print(f"🧰 {len(tools.tools)} Tools disponibles:")
                    for t in tools.tools:
                        print(f"  - {t.name}: {t.description}")

                    if not tools.tools:
                        print("⚠️ No hay workflows MCP publicados")
                        return

                    # Ejecutar búsqueda de workflows como ejemplo
                    tool_name = "search_workflows"
                    print(f"\n▶ Ejecutando: {tool_name}")

                    result = await session.call_tool(
                        tool_name,
                        arguments={}
                    )

                    print("\n📤 Resultado:")
                    print(result)
                    
    except httpx.ConnectError:
        print("❌ Error de conexión: No se puede conectar al servidor n8n")
        print(f"   URL: {url}")
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
