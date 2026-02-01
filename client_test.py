import asyncio
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Cargar variables de entorno
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

async def main():
    api_token = os.getenv("N8N_API_TOKEN")
    if not api_token:
        print("Error: N8N_API_TOKEN no encontrado en .env")
        return

    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    mcp_url = os.getenv("N8N_MCP_URL", "https://eco.dxarte.org/mcp-server/http")

    async with httpx.AsyncClient(
        headers=headers,
        timeout=None  # ← SIN TIMEOUT PARA STREAM
    ) as http_client:

        async with streamable_http_client(
            mcp_url,
            http_client=http_client,
        ) as (read, write, close):

            async with ClientSession(read, write) as session:
                await session.initialize()

                import sys
                if sys.platform == "win32":
                    import io
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

                print("\n[OK] Conectado al MCP de n8n\n")

                tools = await session.list_tools()
                print(f"🧰 {len(tools.tools)} Tools disponibles:")
                for t in tools.tools:
                    print(f"  - {t.name}: {t.description}")

                if not tools.tools:
                    print("⚠️ No hay workflows MCP publicados")
                    return

                tool_name = tools.tools[0].name
                print(f"\n▶ Ejecutando: {tool_name}")

                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "input": "Hola desde antigravity"
                    }
                )

                print("\n📤 Resultado:")
                print(result)

asyncio.run(main())
