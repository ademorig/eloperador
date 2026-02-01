import asyncio
import httpx
import json
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv
from pathlib import Path

async def main():
    load_dotenv(Path(__file__).parent / '.env')
    url = os.getenv('N8N_MCP_URL')
    token = os.getenv('N8N_API_TOKEN')

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(headers=headers, timeout=None) as http_client:
        async with streamable_http_client(
            url,
            http_client=http_client,
        ) as (read, write, close):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("Searching for workflows with tag 'mcp'...")
                result = await session.call_tool(
                    "search_workflows",
                    arguments={"tags": ["mcp"]}
                )
                print(result)

if __name__ == "__main__":
    asyncio.run(main())
