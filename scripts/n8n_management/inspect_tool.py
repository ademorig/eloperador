import asyncio
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImU5NzZiYTAyLWNlY2MtNDZlYy05MTJlLTJjZWQ4MDI1NDZiOCIsImlhdCI6MTc2OTczMDI4MX0.GUAdcdOsel7HaM-a_n4s8ctrLq8-C13d2GI-wdBCTT8"
    }

    async with httpx.AsyncClient(headers=headers, timeout=None) as http_client:
        async with streamable_http_client(
            "https://eco.dxarte.org/mcp-server/http",
            http_client=http_client,
        ) as (read, write, close):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                for t in tools.tools:
                    if t.name == "execute_workflow":
                        print(f"Tool: {t.name}")
                        print(f"Input Schema: {t.inputSchema}")

if __name__ == "__main__":
    asyncio.run(main())
