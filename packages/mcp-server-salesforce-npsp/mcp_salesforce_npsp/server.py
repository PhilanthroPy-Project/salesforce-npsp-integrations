"""MCP server exposing Salesforce NPSP donor data as tools.

Wraps :class:`npsp_core.SalesforceNPSPClient`. Credentials come from the
SF_USERNAME / SF_PASSWORD / SF_TOKEN env vars (and SF_DOMAIN, default 'login').
Run with: ``salesforce-npsp-mcp`` (stdio transport).
"""

import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from npsp_core import SalesforceNPSPClient

mcp = FastMCP("salesforce-npsp")

_client: Optional[SalesforceNPSPClient] = None


def get_client() -> SalesforceNPSPClient:
    """Lazily build one client from env vars (cached for the process)."""
    global _client
    if _client is None:
        _client = SalesforceNPSPClient(domain=os.environ.get("SF_DOMAIN", "login"))
    return _client


def fetch_donors(
    soql_filter: str = "npo02__TotalOppAmount__c > 0",
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Fetch NPSP donors matching a SOQL WHERE clause.

    Args:
        soql_filter: SOQL WHERE clause applied to the Contact object,
            e.g. "npo02__TotalOppAmount__c > 5000".
        limit: Maximum donors to return (default 100).

    Returns a list of {"text", "metadata"} donor records.
    """
    return get_client().load_donors(soql_filter=soql_filter, limit=limit)


def fetch_donor(contact_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single donor by Salesforce Contact ID.

    Returns the {"text", "metadata"} record, or null if not found.
    """
    records = get_client().load_donors(contact_ids=[contact_id])
    return records[0] if records else None


# Register the plain functions as MCP tools (kept plain so they stay unit-testable).
mcp.tool()(fetch_donors)
mcp.tool()(fetch_donor)


def main() -> None:
    """Console-script entrypoint: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
