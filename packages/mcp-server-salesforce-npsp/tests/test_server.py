"""Tests for the Salesforce NPSP MCP server tools."""

from unittest.mock import MagicMock

import mcp_salesforce_npsp.server as server

MOCK_CONTACTS = [
    {
        "Id": "003XXXXXXXXXXXXXXX",
        "FirstName": "Jane",
        "LastName": "Smith",
        "Email": "jane@example.org",
        "npo02__TotalOppAmount__c": 50000.0,
        "npo02__NumberOfClosedOpps__c": 5.0,
        "npo02__LastCloseDate__c": "2024-02-15",
        "npo02__FirstCloseDate__c": "2018-06-01",
        "npo02__AverageAmount__c": 10000.0,
        "npo02__LargestAmount__c": 25000.0,
        "npsp__Primary_Affiliation__r": {"Name": "City Hospital"},
        "npsp__Soft_Credit_Total__c": 5000.0,
        "npsp__Planned_Giving_Count__c": 1.0,
        "LastActivityDate": "2023-08-01",
    }
]


def _install_fake_client(monkeypatch, records=MOCK_CONTACTS):
    from npsp_core import SalesforceNPSPClient

    client = SalesforceNPSPClient(username="u", password="p", security_token="t")
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {"records": records}
    client._sf = mock_sf
    client.include_opportunities = False
    monkeypatch.setattr(server, "_client", client)
    return client


def test_fetch_donors(monkeypatch):
    _install_fake_client(monkeypatch)
    result = server.fetch_donors(limit=10)
    assert len(result) == 1
    assert result[0]["metadata"]["donor_name"] == "Jane Smith"
    assert set(result[0].keys()) == {"text", "metadata"}


def test_fetch_donor_found(monkeypatch):
    _install_fake_client(monkeypatch)
    rec = server.fetch_donor("003XXXXXXXXXXXXXXX")
    assert rec is not None
    assert rec["metadata"]["donor_id"] == "003XXXXXXXXXXXXXXX"


def test_fetch_donor_not_found(monkeypatch):
    _install_fake_client(monkeypatch, records=[])
    assert server.fetch_donor("003NOPE") is None


def test_tools_registered():
    # Both tools must be exposed to MCP clients.
    names = {t.name for t in server.mcp._tool_manager.list_tools()}
    assert {"fetch_donors", "fetch_donor"} <= names
