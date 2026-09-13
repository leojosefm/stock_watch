# Stock Monitor MCP Server

This project exposes the existing FastAPI app as an MCP server so MCP clients can call app tools with natural language.

## What it does

The MCP server wraps FastAPI endpoints for:

* users
* companies
* watchlist
* PEGY ratio
* price history

## Local setup

### Python dependencies

Install the Python packages used by the MCP server:

```bash
pip install -r requirements.txt
pip install httpx "mcp[cli]"
```

### Node.js / npx

MCP Inspector requires `npx`, so Node.js and npm must be installed on the machine.

If you use WSL, install a recent Node version there. For example with `nvm`:

```bash
nvm install --lts
nvm use --lts
```

Verify:

```bash
node -v
npm -v
npx -v
```

## Running the services

Start the FastAPI app and the MCP server, then open the MCP Inspector in your browser.

### Start MCP Inspector

Run:

```bash
mcp dev mcp_server.py
```

This opens the Inspector UI and gives you a local URL in the browser.

## Testing with MCP Inspector

1. Open the Inspector in your browser.
2. Connect to the MCP server.
3. Use the **Tools** tab to call tools such as:

   * `create_user`
   * `get_user_id`
   * `add_to_watchlist`
   * `get_watchlist`
   * `refresh_pegy`
   * `list_companies`
   * `get_pegy_ratio`
   * `get_price_history`

### Example test flow

* Create a user
* Add a company to the watchlist
* Fetch the watchlist
* Refresh PEGY values
* Fetch the watchlist again

## Notes

* `get_watchlist` is working.
* `get_user_id` may need URL encoding for email addresses.
* The MCP server is a thin wrapper and does not add new business logic.
