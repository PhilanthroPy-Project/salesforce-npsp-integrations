# MCP Server — Salesforce NPSP

A [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes
Salesforce **Nonprofit Success Pack (NPSP)** donor data as tools any MCP client
(Claude, CrewAI, etc.) can call.

**NPSP-aware**: understands `npo02__` / `npsp__` fields and returns readable
donor profiles — giving totals, gift history, engagement — not raw JSON.

## Install

```bash
pip install mcp-server-salesforce-npsp
```

## Tools

| Tool | Description |
| --- | --- |
| `fetch_donors(soql_filter, limit)` | Fetch NPSP donors matching a SOQL WHERE clause. |
| `fetch_donor(contact_id)` | Fetch one donor by Salesforce Contact ID. |

Each returns `{"text", "metadata"}` records.

## Configure (Claude Desktop / any MCP client)

```json
{
  "mcpServers": {
    "salesforce-npsp": {
      "command": "salesforce-npsp-mcp",
      "env": {
        "SF_USERNAME": "you@yourorg.org",
        "SF_PASSWORD": "your_password",
        "SF_TOKEN": "your_security_token",
        "SF_DOMAIN": "login"
      }
    }
  }
}
```

Then ask: *"Which major-gift donors haven't been contacted in 6 months?"*
