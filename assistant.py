import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters, stdio_client

load_dotenv()

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def main():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools

            gemini_tools = []
            for t in mcp_tools:
                gemini_tools.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                })

            question = input("Ask about your expenses: ")

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[{"function_declarations": gemini_tools}],
                ),
            )

            function_calls = response.function_calls
            if function_calls:
                call = function_calls[0]
                print(f"\n[Gemini chose to call: {call.name} with {call.args}]")
                result = await session.call_tool(call.name, call.args)
                tool_output = result.content[0].text

                followup = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=f"The user asked: '{question}'. The tool '{call.name}' returned: '{tool_output}'. Answer the user's question in plain English using this data.",
                )
                print("\nAnswer:", followup.text)
            else:
                print("\nAnswer:", response.text)

asyncio.run(main())