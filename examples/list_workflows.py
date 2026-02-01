"""
Ejemplo: Listar workflows disponibles en n8n.

Este script muestra cómo buscar y listar workflows usando la herramienta
'search_workflows' del servidor MCP.
"""

import asyncio
import httpx
import sys
import os
import io
import json
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


async def list_all_workflows():
    """Lista todos los workflows disponibles."""
    
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
                
                print("🔍 Buscando workflows...\n")
                
                # Llamar a la herramienta search_workflows
                result = await session.call_tool(
                    "search_workflows",
                    arguments={}  # Sin filtros = todos los workflows
                )
                
                # Parsear el resultado
                data = json.loads(result.content[0].text)
                workflows = data.get('data', [])
                count = data.get('count', 0)
                
                if count == 0:
                    print("📭 No hay workflows disponibles")
                    return
                
                print(f"📋 {count} workflow(s) encontrado(s):\n")
                
                for i, wf in enumerate(workflows, 1):
                    status = "🟢 Activo" if wf.get('active') else "⚪ Inactivo"
                    print(f"{i}. {wf.get('name', 'Sin nombre')}")
                    print(f"   ID: {wf.get('id')}")
                    print(f"   Estado: {status}")
                    
                    if wf.get('tags'):
                        print(f"   Tags: {', '.join(wf['tags'])}")
                    
                    if wf.get('updatedAt'):
                        print(f"   Última actualización: {wf['updatedAt']}")
                    
                    print()


async def search_workflows_by_name(name: str):
    """Busca workflows por nombre."""
    
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
                
                print(f"🔍 Buscando workflows con '{name}'...\n")
                
                result = await session.call_tool(
                    "search_workflows",
                    arguments={"name": name}
                )
                
                data = json.loads(result.content[0].text)
                workflows = data.get('data', [])
                count = data.get('count', 0)
                
                if count == 0:
                    print(f"📭 No se encontraron workflows con '{name}'")
                    return
                
                print(f"📋 {count} workflow(s) encontrado(s):\n")
                
                for wf in workflows:
                    print(f"• {wf.get('name')} (ID: {wf.get('id')})")


if __name__ == "__main__":
    # Ejemplo 1: Listar todos
    print("=" * 60)
    print("EJEMPLO 1: Listar todos los workflows")
    print("=" * 60 + "\n")
    asyncio.run(list_all_workflows())
    
    # Ejemplo 2: Buscar por nombre (descomenta y ajusta el nombre)
    # print("\n" + "=" * 60)
    # print("EJEMPLO 2: Buscar workflows por nombre")
    # print("=" * 60 + "\n")
    # asyncio.run(search_workflows_by_name("test"))
