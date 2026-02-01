"""
Ejemplo: Ejecutar un workflow de n8n.

Este script demuestra cómo ejecutar un workflow específico,
con o sin parámetros de entrada.
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


async def execute_workflow(workflow_id: str, input_data: dict = None):
    """
    Ejecuta un workflow de n8n.
    
    Args:
        workflow_id: ID del workflow a ejecutar
        input_data: Datos de entrada opcionales (dict)
    """
    
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
                
                print(f"▶️  Ejecutando workflow: {workflow_id}")
                
                if input_data:
                    print(f"📥 Con datos de entrada: {json.dumps(input_data, indent=2)}")
                
                print("\n⏳ Procesando...\n")
                
                # Preparar argumentos
                args = {"workflowId": workflow_id}
                if input_data:
                    args["input"] = input_data
                
                try:
                    # Ejecutar el workflow
                    result = await session.call_tool(
                        "execute_workflow",
                        arguments=args
                    )
                    
                    print("✅ Workflow ejecutado exitosamente\n")
                    print("📤 Resultado:")
                    print("-" * 60)
                    
                    # Mostrar el resultado
                    result_text = result.content[0].text
                    
                    # Intentar formatear como JSON si es posible
                    try:
                        result_json = json.loads(result_text)
                        print(json.dumps(result_json, indent=2, ensure_ascii=False))
                    except:
                        print(result_text)
                    
                    print("-" * 60)
                    
                except Exception as e:
                    print(f"❌ Error al ejecutar workflow: {e}")


async def get_workflow_details_first(workflow_id: str):
    """
    Obtiene detalles del workflow antes de ejecutarlo.
    Útil para conocer qué parámetros espera.
    """
    
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
                
                print(f"ℹ️  Obteniendo detalles del workflow: {workflow_id}\n")
                
                result = await session.call_tool(
                    "get_workflow_details",
                    arguments={"workflowId": workflow_id}
                )
                
                data = json.loads(result.content[0].text)
                
                print(f"📄 Nombre: {data.get('name')}")
                print(f"🔧 Nodos: {len(data.get('nodes', []))}")
                
                if data.get('triggerDetails'):
                    trigger = data['triggerDetails']
                    print(f"\n🎯 Trigger:")
                    print(f"   Tipo: {trigger.get('type')}")
                    if trigger.get('description'):
                        print(f"   Descripción: {trigger['description']}")
                
                print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # IMPORTANTE: Reemplaza 'YOUR_WORKFLOW_ID' con un ID real de tu n8n
    WORKFLOW_ID = "YOUR_WORKFLOW_ID"
    
    # Ejemplo 1: Ver detalles primero
    print("=" * 60)
    print("PASO 1: Ver detalles del workflow")
    print("=" * 60 + "\n")
    asyncio.run(get_workflow_details_first(WORKFLOW_ID))
    
    # Ejemplo 2: Ejecutar sin parámetros
    print("=" * 60)
    print("PASO 2: Ejecutar workflow sin parámetros")
    print("=" * 60 + "\n")
    asyncio.run(execute_workflow(WORKFLOW_ID))
    
    # Ejemplo 3: Ejecutar con parámetros (descomenta y ajusta según tu workflow)
    # print("\n" + "=" * 60)
    # print("PASO 3: Ejecutar workflow con parámetros")
    # print("=" * 60 + "\n")
    # 
    # input_data = {
    #     "nombre": "Juan",
    #     "email": "juan@example.com",
    #     "mensaje": "Hola desde Python!"
    # }
    # 
    # asyncio.run(execute_workflow(WORKFLOW_ID, input_data))
