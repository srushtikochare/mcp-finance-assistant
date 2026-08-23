import asyncio
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters, stdio_client

load_dotenv()

import sys

server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
)

async def ask_question(question, history):
    api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    context_lines = []
    for turn in history[-5:]:
        context_lines.append(f"User: {turn['question']}")
        context_lines.append(f"Assistant: {turn['answer']}")
    context_text = "\n".join(context_lines)

    full_prompt = (
        f"{context_text}\nUser: {question}" if context_text else question
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            gemini_tools = []
            for t in tools_result.tools:
                gemini_tools.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                })

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"function_declarations": gemini_tools}],
                ),
            )

            function_calls = response.function_calls
            if function_calls:
                call = function_calls[0]
                result = await session.call_tool(call.name, call.args)
                tool_output = result.content[0].text

                followup = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=f"{context_text}\nThe user asked: '{question}'. The tool '{call.name}' returned: '{tool_output}'. Answer in plain English using this data, considering the earlier conversation if relevant.",
                )
                return followup.text, call.name
            else:
                return response.text, None

st.set_page_config(page_title="Personal Finance Assistant", page_icon="💰")
st.title("💰 Personal Finance Assistant")
st.caption("Ask questions about your expenses in plain English — powered by MCP + Gemini")

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_input("Ask a question:", placeholder="How much did I spend on food?")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        answer, tool_used = asyncio.run(ask_question(question, st.session_state.history))
    st.session_state.history.append({"question": question, "answer": answer})
    st.success(answer)
    if tool_used:
        st.caption(f"🔧 Tool used: `{tool_used}`")

if st.session_state.history:
    st.divider()
    st.subheader("💬 Conversation History")
    for turn in reversed(st.session_state.history):
        st.markdown(f"**You:** {turn['question']}")
        st.markdown(f"**Assistant:** {turn['answer']}")

    if st.button("Clear conversation"):
        st.session_state.history = []
        st.rerun()

st.divider()
st.subheader("📊 Spending Overview")
df = pd.read_csv("expenses.csv")
category_totals = df.groupby("category")["amount"].sum()
st.bar_chart(category_totals)