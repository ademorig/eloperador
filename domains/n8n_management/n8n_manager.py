#!/usr/bin/env python
"""
n8n Manager CLI - Herramienta de línea de comandos para gestionar workflows de n8n vía MCP.

Uso:
    python n8n_manager.py list                    # Listar todos los workflows
    python n8n_manager.py search <query>          # Buscar workflows
    python n8n_manager.py info <workflow-id>      # Ver detalles de un workflow
    python n8n_manager.py run <workflow-id>       # Ejecutar un workflow
    python n8n_manager.py                         # Modo interactivo
"""

import asyncio
import httpx
import sys
import os
import io
import json
from pathlib import Path
from typing import Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv

# Fix Windows UTF-8 encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class N8NManager:
    """Gestor de workflows de n8n vía MCP."""
    
    def __init__(self):
        self.url = os.getenv('N8N_MCP_URL')
        self.token = os.getenv('N8N_API_TOKEN')
        
        if not self.url or not self.token:
            print("❌ Error: N8N_MCP_URL y N8N_API_TOKEN deben estar definidos en .env")
            sys.exit(1)
    
    async def connect(self):
        """Establece conexión con el servidor MCP de n8n."""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        self.http_client = httpx.AsyncClient(headers=headers, timeout=None)
        
        # Store the context manager
        self._stream_context = streamable_http_client(
            self.url,
            http_client=self.http_client,
        )
        
        # Enter the context
        self.read, self.write, self.close = await self._stream_context.__aenter__()
        
        # Create session context
        self._session_context = ClientSession(self.read, self.write)
        self.session = await self._session_context.__aenter__()
        await self.session.initialize()
    
    async def disconnect(self):
        """Cierra la conexión."""
        try:
            if hasattr(self, '_session_context'):
                await self._session_context.__aexit__(None, None, None)
            if hasattr(self, '_stream_context'):
                await self._stream_context.__aexit__(None, None, None)
            if hasattr(self, 'http_client'):
                await self.http_client.aclose()
        except Exception as e:
            print(f"⚠️  Error al cerrar conexión: {e}")
    
    async def list_workflows(self):
        """Lista todos los workflows disponibles."""
        try:
            result = await self.session.call_tool("search_workflows", arguments={})
            data = json.loads(result.content[0].text)
            
            workflows = data.get('data', [])
            count = data.get('count', 0)
            
            if count == 0:
                print("📭 No hay workflows disponibles")
                return
            
            print(f"\n📋 {count} Workflow(s) encontrado(s):\n")
            for wf in workflows:
                status = "🟢" if wf.get('active') else "⚪"
                print(f"{status} {wf.get('name', 'Sin nombre')} (ID: {wf.get('id')})")
                if wf.get('tags'):
                    print(f"   Tags: {', '.join(wf['tags'])}")
                print()
                
        except Exception as e:
            print(f"❌ Error al listar workflows: {e}")
    
    async def search_workflows(self, query: str):
        """Busca workflows por nombre."""
        try:
            result = await self.session.call_tool(
                "search_workflows",
                arguments={"name": query}
            )
            data = json.loads(result.content[0].text)
            
            workflows = data.get('data', [])
            count = data.get('count', 0)
            
            if count == 0:
                print(f"📭 No se encontraron workflows con '{query}'")
                return
            
            print(f"\n🔍 {count} Workflow(s) encontrado(s) con '{query}':\n")
            for wf in workflows:
                status = "🟢" if wf.get('active') else "⚪"
                print(f"{status} {wf.get('name', 'Sin nombre')} (ID: {wf.get('id')})")
                print()
                
        except Exception as e:
            print(f"❌ Error al buscar workflows: {e}")
    
    async def get_workflow_info(self, workflow_id: str):
        """Obtiene información detallada de un workflow."""
        try:
            result = await self.session.call_tool(
                "get_workflow_details",
                arguments={"workflowId": workflow_id}
            )
            data = json.loads(result.content[0].text)
            
            print(f"\n📄 Detalles del Workflow:\n")
            print(f"ID: {data.get('id')}")
            print(f"Nombre: {data.get('name')}")
            print(f"Activo: {'Sí' if data.get('active') else 'No'}")
            
            if data.get('tags'):
                print(f"Tags: {', '.join(data['tags'])}")
            
            if data.get('triggerDetails'):
                print(f"\n🎯 Trigger:")
                trigger = data['triggerDetails']
                print(f"   Tipo: {trigger.get('type', 'N/A')}")
                if trigger.get('description'):
                    print(f"   Descripción: {trigger['description']}")
            
            if data.get('nodes'):
                print(f"\n🔧 Nodos: {len(data['nodes'])}")
            
            print()
                
        except Exception as e:
            print(f"❌ Error al obtener información del workflow: {e}")
    
    async def execute_workflow(self, workflow_id: str, input_data: Optional[dict] = None):
        """Ejecuta un workflow."""
        try:
            args = {"workflowId": workflow_id}
            if input_data:
                args["input"] = input_data
            
            print(f"▶️  Ejecutando workflow {workflow_id}...")
            result = await self.session.call_tool("execute_workflow", arguments=args)
            
            print(f"\n✅ Workflow ejecutado exitosamente\n")
            print("📤 Resultado:")
            print(result.content[0].text)
            print()
                
        except Exception as e:
            print(f"❌ Error al ejecutar workflow: {e}")
    
    async def interactive_mode(self):
        """Modo interactivo con menú."""
        while True:
            print("\n" + "="*50)
            print("🎛️  n8n Manager - Modo Interactivo")
            print("="*50)
            print("\n1. Listar workflows")
            print("2. Buscar workflow")
            print("3. Ver detalles de workflow")
            print("4. Ejecutar workflow")
            print("5. Salir")
            
            choice = input("\nSelecciona una opción (1-5): ").strip()
            
            if choice == "1":
                await self.list_workflows()
            elif choice == "2":
                query = input("Ingresa el término de búsqueda: ").strip()
                await self.search_workflows(query)
            elif choice == "3":
                workflow_id = input("Ingresa el ID del workflow: ").strip()
                await self.get_workflow_info(workflow_id)
            elif choice == "4":
                workflow_id = input("Ingresa el ID del workflow: ").strip()
                use_input = input("¿Quieres enviar datos de entrada? (s/n): ").strip().lower()
                
                input_data = None
                if use_input == 's':
                    print("Ingresa los datos en formato JSON (o presiona Enter para omitir):")
                    json_str = input().strip()
                    if json_str:
                        try:
                            input_data = json.loads(json_str)
                        except json.JSONDecodeError:
                            print("⚠️  JSON inválido, ejecutando sin datos de entrada")
                
                await self.execute_workflow(workflow_id, input_data)
            elif choice == "5":
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")


async def main():
    """Punto de entrada principal."""
    manager = N8NManager()
    
    try:
        await manager.connect()
        
        # Modo CLI
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "list":
                await manager.list_workflows()
            
            elif command == "search":
                if len(sys.argv) < 3:
                    print("❌ Uso: python n8n_manager.py search <query>")
                    return
                query = " ".join(sys.argv[2:])
                await manager.search_workflows(query)
            
            elif command == "info":
                if len(sys.argv) < 3:
                    print("❌ Uso: python n8n_manager.py info <workflow-id>")
                    return
                workflow_id = sys.argv[2]
                await manager.get_workflow_info(workflow_id)
            
            elif command == "run":
                if len(sys.argv) < 3:
                    print("❌ Uso: python n8n_manager.py run <workflow-id> [json-input]")
                    return
                workflow_id = sys.argv[2]
                input_data = None
                if len(sys.argv) > 3:
                    try:
                        input_data = json.loads(sys.argv[3])
                    except json.JSONDecodeError:
                        print("⚠️  JSON inválido, ejecutando sin datos de entrada")
                
                await manager.execute_workflow(workflow_id, input_data)
            
            else:
                print(f"❌ Comando desconocido: {command}")
                print(__doc__)
        
        # Modo interactivo
        else:
            await manager.interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
