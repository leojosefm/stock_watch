"""
Stock Monitor - MCP Server (simple lab version, no auth)

Wraps the existing FastAPI endpoints (/users, /companies) as MCP tools so
an MCP client (MCP Inspector, or any MCP-compatible LLM client on your
own machine) can drive the app via natural language.

This is deliberately the simplest possible version: no OAuth, no tokens,
no allowlists. user_id is passed directly as a tool argument. This is
fine for local, single-user experimentation - NOT something to expose
publicly, since anyone who can reach this server can act as any user_id.

Note: this server can only do what the FastAPI app already exposes.
No new business logic lives here - it's a thin translation layer.
"""

import os
import logging
import httpx
from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stock-monitor-mcp")

# Base URL of the FastAPI service. Overridable via env var so it works
# both in Docker (service name) and locally (localhost).
API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

mcp = MCPServer("stock-monitor")

# Shared async client (reused across calls) - see SETUP.md for why this
# is a singleton instead of a new client per call.
_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=API_BASE, timeout=15.0)
    return _client


async def _handle_response(resp: httpx.Response) -> dict:
    """Normalize FastAPI responses (including HTTPException errors) into
    a consistent shape the LLM can reason about."""
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        message = data.get("detail", data) if isinstance(data, dict) else data
        return {"error": True, "status_code": resp.status_code, "message": message}

    return data


# ---------------------------------------------------------------------------
# User tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def create_user(email: str) -> dict:
    """Create a new user by email. If the email is already registered,
    returns the existing user instead of erroring."""
    client = await get_client()
    resp = await client.post("/users/", json={"email": email})
    return await _handle_response(resp)


@mcp.tool()
async def get_user_id(email: str) -> dict:
    """Look up a user's ID and details by their email address."""
    client = await get_client()
    resp = await client.get(f"/users/{quote(email, safe='')}/id")
    return await _handle_response(resp)


# ---------------------------------------------------------------------------
# Watchlist tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def add_to_watchlist(
    user_id: int,
    company_name: str,
    ticker_symbol: str,
    rsi_threshold: float | None = None,
) -> dict:
    """Add a company to a user's watchlist, optionally with an RSI alert
    threshold. Fails if a pending alert already exists for this user and
    threshold combination."""
    client = await get_client()
    payload = {
        "user_id": user_id,
        "company_name": company_name,
        "ticker_symbol": ticker_symbol,
        "rsi_threshold": rsi_threshold,
    }
    resp = await client.post("/users/watchlist/", json=payload)
    return await _handle_response(resp)


@mcp.tool()
async def get_watchlist(user_id: int) -> dict:
    """Get all watchlist entries (companies + thresholds + PEGY ratios)
    for a given user ID."""
    client = await get_client()
    resp = await client.get(f"/users/watchlist/{user_id}")
    result = await _handle_response(resp)
    if result == []:
        return {"watchlist": [], "note": "No items found. This could mean the user has an empty watchlist, or the user_id does not exist."}
    return result


@mcp.tool()
async def refresh_pegy(user_id: int) -> dict:
    """Refresh PEGY ratios for all watchlist items that don't have one yet,
    for the given user. Returns the updated watchlist. Items that already
    have a PEGY ratio are not re-fetched."""
    client = await get_client()
    resp = await client.post(f"/users/watchlist/{user_id}/refresh-pegy")
    return await _handle_response(resp)


# ---------------------------------------------------------------------------
# Company tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_companies() -> dict:
    """List all companies known to the system (name + ticker symbol)."""
    client = await get_client()
    resp = await client.get("/companies/")
    data = await _handle_response(resp)
    return {"companies": data}


@mcp.tool()
async def create_company(company_name: str, ticker_symbol: str) -> dict:
    """Register a new company with its ticker symbol."""
    client = await get_client()
    # Current API takes these as query params, not a JSON body.
    resp = await client.post(
        "/companies/",
        params={"company_name": company_name, "ticker_symbol": ticker_symbol},
    )
    return await _handle_response(resp)


@mcp.tool()
async def get_pegy_ratio(ticker: str) -> dict:
    """Get the latest PEGY ratio for a given ticker symbol."""
    client = await get_client()
    resp = await client.get(f"/companies/pegy/{ticker}")
    return await _handle_response(resp)


@mcp.tool()
async def get_price_history(ticker: str) -> dict:
    """Get historical closing prices for a given ticker symbol, ordered
    oldest to newest."""
    client = await get_client()
    resp = await client.get(f"/companies/history/{ticker}")
    data = await _handle_response(resp)
    return {"ticker": ticker, "history": data}


if __name__ == "__main__":
    # streamable-http so MCP Inspector (or any client) can connect over
    # localhost without needing a tunnel or any auth setup.
    # host="0.0.0.0" is required inside Docker - the default (127.0.0.1)
    # would only be reachable from inside this container.
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8100,
        streamable_http_path="/mcp",
    )