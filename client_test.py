import asyncio
from mcp import ClientSession, StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("--- Testing a category that doesn't exist ---")
            result = await session.call_tool("get_total_by_category", {"category": "entertainment"})
            print(result)

            print("\n--- Testing a negative amount ---")
            result2 = await session.call_tool("add_expense", {
                "date": "2026-08-21",
                "category": "food",
                "amount": -100,
                "description": "Invalid test"
            })
            print(result2)

            print("\n--- Testing an empty category ---")
            result3 = await session.call_tool("get_total_by_category", {"category": ""})
            print(result3)

asyncio.run(main())