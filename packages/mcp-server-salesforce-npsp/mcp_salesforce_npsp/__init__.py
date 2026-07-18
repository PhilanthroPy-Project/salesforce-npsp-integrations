"""MCP server for Salesforce Nonprofit Success Pack (NPSP) donor data."""

from mcp_salesforce_npsp.server import fetch_donor, fetch_donors, main, mcp

__all__ = ["mcp", "main", "fetch_donors", "fetch_donor"]
