import asyncio
import os
import sys
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters, stdio_client

load_dotenv()

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

    today_str = date.today().isoformat()
    instruction = (
        f"Today's date is {today_str}. "
        "If the user wants to add an expense but doesn't specify a category, "
        "first call get_existing_categories, then infer the single most fitting "
        "category from the description before calling add_expense. Use today's "
        f"actual date ({today_str}) if no date is given — never guess or invent a date."
    )

    full_prompt = (
        f"{context_text}\n{instruction}\nUser: {question}"
        if context_text else f"{instruction}\nUser: {question}"
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

            tools_used = []
            current_prompt = full_prompt
            max_steps = 3

            for _ in range(max_steps):
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=current_prompt,
                    config=types.GenerateContentConfig(
                        tools=[{"function_declarations": gemini_tools}],
                    ),
                )
                function_calls = response.function_calls
                if not function_calls:
                    tool_summary = ", ".join(tools_used) if tools_used else None
                    return response.text, tool_summary

                call = function_calls[0]
                tools_used.append(call.name)
                result = await session.call_tool(call.name, call.args)
                tool_output = result.content[0].text

                current_prompt = (
                    f"{current_prompt}\n"
                    f"[Called tool '{call.name}' with {dict(call.args)}, result: '{tool_output}']\n"
                    f"If another tool call is needed to finish the user's request, call it now. "
                    f"Otherwise, answer the user's original question in plain English."
                )

            followup = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"{current_prompt}\nAnswer the user's original question in plain English now.",
            )
            tool_summary = ", ".join(tools_used) if tools_used else None
            return followup.text, tool_summary

async def check_all_anomalies(categories):
    alerts = []
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for category in categories:
                result = await session.call_tool("detect_anomaly", {"category": category})
                text = result.content[0].text
                if "⚠️" in text:
                    alerts.append(text)
    return alerts

def get_categories():
    conn = sqlite3.connect("expenses.db")
    categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM expenses").fetchall()]
    conn.close()
    return categories

st.set_page_config(page_title="Personal Finance Assistant", page_icon="💰")
st.title("💰 Personal Finance Assistant")
st.caption("Ask questions about your expenses in plain English — powered by MCP + Gemini")

if "alerts_checked" not in st.session_state:
    with st.spinner("Checking for spending anomalies..."):
        categories = get_categories()
        alerts = asyncio.run(check_all_anomalies(categories))
        st.session_state.alerts = alerts
        st.session_state.alerts_checked = True

if st.session_state.get("alerts"):
    st.subheader("🚨 Automatic Insights")
    for alert in st.session_state.alerts:
        st.warning(alert)
    st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_input(
    "Ask a question:",
    placeholder="Add an expense of 200 for Uber to the airport",
)

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        answer, tool_used = asyncio.run(ask_question(question, st.session_state.history))
    st.session_state.history.append({"question": question, "answer": answer})
    st.success(answer)
    if tool_used:
        st.caption(f"🔧 Tool(s) used: `{tool_used}`")

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
conn = sqlite3.connect("expenses.db")
df = pd.read_sql("SELECT * FROM expenses", conn)
conn.close()
category_totals = df.groupby("category")["amount"].sum()
st.bar_chart(category_totals)