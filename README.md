# 💰 Personal Finance Assistant — MCP + Gemini

An AI-powered personal finance assistant that allows users to analyze and manage expenses using **natural language**. The system combines **Google Gemini, Model Context Protocol (MCP), SQL data, and machine learning tools** to transform a conversational request into real database queries, predictions, and anomaly detection.

🔗 **Live Demo:** https://mcp-finance-assistant-z6txg3k6xparsajcsvftrr.streamlit.app/

---

## 🚀 Overview

Traditional expense trackers require users to navigate filters, categories, and dashboards manually.

This project provides a conversational interface where users can simply ask:

* *"How much did I spend on food this month?"*
* *"Compare my spending in August and July."*
* *"Show me my recent expenses."*
* *"Add an expense of ₹250 for Uber to the airport."*
* *"What will I spend on food next month?"*

Instead of generating answers from predefined responses, **Gemini determines which application tool is required, invokes it through MCP, receives the actual result, and generates a natural-language response.**

The system also performs **automatic anomaly detection** to identify unusual spending patterns.

---

## 🎯 Key Objectives

* Enable natural-language interaction with structured financial data.
* Integrate an LLM with real application tools using **Model Context Protocol (MCP)**.
* Provide expense analysis using a SQL database.
* Apply machine learning for spending forecasting and anomaly detection.
* Support multi-step tool execution for requests requiring multiple operations.
* Validate inputs and handle tool-level errors reliably.
* Provide automated tests for core financial calculations and tool behavior.

---

## 🏗️ System Architecture

```text
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                     ┌────────────────────┐
                     │   Streamlit UI     │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌────────────────────┐
                     │   Google Gemini   │
                     │  Tool Selection   │
                     └─────────┬──────────┘
                               │
                         MCP Protocol
                               │
                               ▼
                     ┌────────────────────┐
                     │    MCP Server      │
                     │     server.py      │
                     └─────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐  ┌──────────────┐
       │   SQLite   │   │ Forecasting │  │   Anomaly    │
       │  Database  │   │     ML      │  │  Detection   │
       └────────────┘   └─────────────┘  └──────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                         Tool Results
                               │
                               ▼
                     ┌────────────────────┐
                     │   Google Gemini    │
                     │ Response Generation│
                     └─────────┬──────────┘
                               │
                               ▼
                         Natural Language
                            Response
```

### Multi-step Tool Calling

Some requests require more than one operation.

For example:

> *"Add ₹250 for Uber to the airport."*

The system can perform a sequence such as:

```text
User Request
     ↓
Identify missing category
     ↓
Retrieve available categories
     ↓
Gemini determines appropriate category
     ↓
Add expense to database
     ↓
Return confirmation
```

This demonstrates how an LLM can interact with application capabilities rather than simply generating text.

---

## ✨ Features

### 1. Natural-Language Expense Analysis

Users can ask questions about their expenses without manually writing SQL queries or navigating filters.

Example:

```text
"How much did I spend on food this month?"
```

The system retrieves the relevant financial data and returns the result in natural language.

### 2. MCP-Based Tool Integration

The application exposes financial operations as MCP tools that Gemini can discover and invoke.

The project currently provides **7 tools** for:

* Expense totals
* Monthly comparisons
* Recent expense retrieval
* Adding expenses
* Category retrieval
* Spending forecasts
* Anomaly detection

### 3. Machine Learning Forecasting

The `forecast_next_month` tool uses **scikit-learn Linear Regression** to estimate future spending based on historical spending trends.

This allows the assistant to answer questions such as:

```text
"What will I spend on food next month?"
```

### 4. Anomaly Detection

The system uses **Isolation Forest**, an unsupervised machine-learning algorithm, to identify potentially unusual spending patterns.

Instead of relying only on a manually defined spending threshold, the model identifies observations that differ from the learned pattern.

### 5. LLM-Based Categorization

When an expense is entered without an explicit category, Gemini can infer the appropriate category using available category information.

Example:

```text
"Add ₹250 for Uber to the airport."
```

The system can identify the relevant category before storing the transaction.

### 6. Proactive Insights

The application performs an automatic anomaly check when the interface loads, allowing unusual transactions to be highlighted without requiring the user to explicitly ask.

### 7. Conversational Context

Follow-up questions can use information from the ongoing conversation.

Example:

```text
User: How much did I spend on food in August?

Assistant: ₹4,850.

User: What about July?

Assistant: ₹4,120.
```

### 8. Input Validation and Error Handling

Tools validate inputs and handle invalid requests before performing database or model operations.

### 9. Automated Testing

The project includes a `pytest` test suite covering:

* Financial calculations
* Error handling
* Tool behavior
* Machine-learning tool execution

---

## 📊 Dataset

The application uses **240+ transaction records**, including **231 records imported and cleaned from a public Kaggle personal-expense dataset**.

The dataset is stored and queried through SQLite for application-level financial analysis.

---

## 🛠️ Tech Stack

| Category            | Technology                   |
| ------------------- | ---------------------------- |
| Language            | Python                       |
| LLM                 | Google Gemini                |
| AI Tool Integration | Model Context Protocol (MCP) |
| Database            | SQLite                       |
| Machine Learning    | scikit-learn                 |
| Forecasting         | Linear Regression            |
| Anomaly Detection   | Isolation Forest             |
| Frontend            | Streamlit                    |
| Testing             | pytest                       |
| Logging             | Python logging               |

---

## 🧪 Testing

Run the test suite using:

```bash
pytest test_server.py -v
```

The tests verify core calculations, error handling, and ML-related tool behavior against known data.

---

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/srushtikochare/mcp-finance-assistant
cd mcp-finance-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API key

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run the application

```bash
streamlit run app.py
```

---

## 🧠 Technical Challenge

During development, the MCP Python SDK had changed from the API structure described in several available examples.

Instead of relying on outdated documentation, I inspected the installed package and its available API surface to determine the appropriate server implementation.

This required adapting the implementation to the **actual installed SDK version** and testing the integration against the current API.

This experience highlighted an important practical aspect of AI application development: **LLM and AI infrastructure libraries evolve rapidly, so applications need to be developed against the actual SDK/API behavior rather than relying solely on older tutorials.**

---

## 🔐 Current Limitations

This is currently designed as a **single-user personal finance application**.

It does not yet include:

* User authentication
* Separate financial profiles
* Receipt/statement OCR
* Advanced forecasting models for strong seasonal patterns
* Distributed deployment
* Advanced API rate limiting

These are potential directions for future development.

---

## 🔮 Future Improvements

* Multi-user authentication and isolated financial profiles
* Receipt and bank-statement OCR
* More advanced forecasting models
* Automatic recurring-expense detection
* Interactive spending dashboards
* Retry mechanisms with exponential backoff
* More extensive evaluation datasets
* Containerized deployment

---

## 💡 What This Project Demonstrates

This project demonstrates practical experience with:

* LLM tool calling
* Model Context Protocol (MCP)
* Agent-style application workflows
* SQL database integration
* Machine-learning integration
* Natural-language interfaces
* Anomaly detection
* Time-series-style spending forecasting
* API integration
* Input validation and error handling
* Automated testing
* Application logging
* Debugging evolving AI SDKs

---

## 👩‍💻 Author

**Srushti Kochare**
B.Tech — Artificial Intelligence & Data Science
Yeshwantrao Chavan College of Engineering (YCCE), Nagpur

GitHub: https://github.com/srushtikochare
