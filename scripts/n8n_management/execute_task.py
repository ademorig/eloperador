import asyncio
import httpx
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImU5NzZiYTAyLWNlY2MtNDZlYy05MTJlLTJjZWQ4MDI1NDZiOCIsImlhdCI6MTc2OTczMDI4MX0.GUAdcdOsel7HaM-a_n4s8ctrLq8-C13d2GI-wdBCTT8"
    }

    workflow_id = "qGTh7sd-DwFvTGHt660Kx"
    user_prompt = "Dime el número de correos en mi bandeja de entrada de Gmail."

    async with httpx.AsyncClient(headers=headers, timeout=None) as http_client:
        async with streamable_http_client(
            "https://eco.dxarte.org/mcp-server/http",
            http_client=http_client,
        ) as (read, write, close):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print(f"Executing workflow {workflow_id}...")
                result = await session.call_tool(
                    "execute_workflow",
                    arguments={
                        "workflowId": workflow_id,
                        "parameters": {
                            "input": user_prompt
                        }
                    }
                )
                print("\n--- RESULT ---")
                print(result)

if __name__ == "__main__":
    asyncio.run(main())
