# 💰 Personal Finance Assistant — MCP + Gemini

An AI-powered finance assistant that lets you ask questions about your expenses in plain English. Built using the **Model Context Protocol (MCP)** to connect Google's Gemini to real tools — a SQL database, forecasting models, and anomaly detection — instead of a scripted chatbot that only knows how to talk.

**🔗 Live demo:** [mcp-finance-assistant-z6txg3k6xparsajcsvftrr.streamlit.app](https://mcp-finance-assistant-z6txg3k6xparsajcsvftrr.streamlit.app)

---

## What it does

Ask it things like:
- *"How much did I spend on food this month?"*
- *"Compare my spending in August vs July"*
- *"Add an expense of 250 for Uber to the airport"* — it infers the category itself
- *"What will I spend on food next month?"* — real ML forecasting, not a guess

It also **proactively** flags unusual spending the moment the page loads, without being asked.

## Why MCP

Most AI finance-tracker demos hardcode a chatbot's responses or bolt an LLM onto static data. This project instead builds a real **MCP server** — a standardized way (introduced by Anthropic) for an AI model to discover and call real tools. Gemini reads the available tools, decides which one(s) it needs, calls them through the MCP protocol, and reasons over the actual results. It's the same pattern used by production AI agent systems, not a toy simulation.

## Architecture

```
User question → Streamlit UI → Gemini (decides which tool to call)
                                      ↓
                          MCP Server (server.py)
                                      ↓
                          SQLite Database (real transaction data)
                                      ↓
                     Tool result → back to Gemini → plain-English answer
```

For multi-step requests (like adding an expense without a category), Gemini chains multiple tool calls — first fetching existing categories, then inferring the right one, then adding the expense — up to 3 steps per question.

## Features

- **7 MCP tools**: query totals, compare months, list recent expenses, add expenses, get categories, forecast spending, detect anomalies
- **Real ML, not rules**: `forecast_next_month` uses scikit-learn `LinearRegression` on historical trends; `detect_anomaly` uses an unsupervised `IsolationForest` model instead of a hardcoded threshold
- **LLM-inferred categorization**: describe an expense in plain English and Gemini picks the right category on its own, chaining tool calls to do it
- **Proactive insights**: automatic anomaly checks run on page load, no question needed
- **Conversation memory**: follow-up questions understand context from earlier in the chat
- **Real data**: 240+ real transaction records, including 231 imported and cleaned from a public Kaggle personal-expense dataset
- **Production practices**: full error handling and input validation on every tool, structured logging (`app.log`), and an 8-test `pytest` suite verifying calculations against known data

## Tech stack

Python · MCP SDK · Google Gemini (`google-genai`) · SQLite · scikit-learn · Streamlit · pytest

## Running it locally

```bash
git clone https://github.com/srushtikochare/mcp-finance-assistant
cd mcp-finance-assistant
pip install -r requirements.txt
```

Create a `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

Then run:
```bash
streamlit run app.py
```

## Running the tests

```bash
pytest test_server.py -v
```

8 tests covering correct sums, error handling, and ML tool behavior — all passing.

## A real challenge I hit

The MCP Python SDK's structure had changed since most available documentation was written — the class I expected (`FastMCP`) didn't exist in the installed version. Rather than guess, I inspected the actual installed package (`dir(mcp.server)`) to find the correct current class (`MCPServer`) and API surface. Debugging against an evolving library with incomplete docs, instead of a stable tutorial-friendly one, was the most valuable part of building this.

## Possible next steps

- Multi-user support with individual logins
- Receipt/statement OCR upload for automatic expense entry
- Retry logic with backoff for external API resilience

## Author

**Srushti Kochare** — B.Tech Artificial Intelligence & Data Science, YCCE Nagpur