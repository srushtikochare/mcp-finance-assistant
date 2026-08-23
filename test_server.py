import os
import pytest

os.environ["FINANCE_DB_PATH"] = "test_expenses.db"

from mcp import ClientSession, StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={**os.environ, "FINANCE_DB_PATH": "test_expenses.db"},
)

@pytest.mark.asyncio
async def test_get_total_by_category_correct_sum():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_total_by_category", {"category": "food"})
            text = result.content[0].text
            # Known total: 100 + 200 + 50 = 350
            assert "350" in text

@pytest.mark.asyncio
async def test_get_total_by_category_with_month_filter():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_total_by_category", {"category": "food", "month": "2026-08"})
            text = result.content[0].text
            # Only August food: 100 + 200 = 300 (July's 50 excluded)
            assert "300" in text

@pytest.mark.asyncio
async def test_unknown_category_returns_clean_message():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_total_by_category", {"category": "made_up_category_xyz"})
            text = result.content[0].text
            assert "No expenses found" in text

@pytest.mark.asyncio
async def test_negative_amount_rejected():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("add_expense", {
                "date": "2026-08-22", "category": "food", "amount": -50, "description": "bad"
            })
            text = result.content[0].text
            assert "Error" in text

@pytest.mark.asyncio
async def test_empty_category_rejected():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_total_by_category", {"category": ""})
            text = result.content[0].text
            assert "Error" in text

@pytest.mark.asyncio
async def test_get_existing_categories_returns_known_categories():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_existing_categories", {})
            text = result.content[0].text
            # From our test data: food, transport
            assert "food" in text
            assert "transport" in text

@pytest.mark.asyncio
async def test_forecast_with_known_data():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Test data has July (50) and August (100+200=300) for food
            # Average of the two months: (50 + 300) / 2 = 175
            result = await session.call_tool("forecast_next_month", {"category": "food"})
            text = result.content[0].text
            assert "175" in text

@pytest.mark.asyncio
async def test_detect_anomaly_with_insufficient_data():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("detect_anomaly", {"category": "food"})
            text = result.content[0].text
            assert "Not enough historical data" in text