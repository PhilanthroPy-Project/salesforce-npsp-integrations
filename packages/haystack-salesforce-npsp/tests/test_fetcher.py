"""Tests for the Haystack SalesforceNPSPFetcher component."""

from unittest.mock import MagicMock

from haystack import Document

from haystack_salesforce_npsp import SalesforceNPSPFetcher

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


def _fetcher_with_mock():
    fetcher = SalesforceNPSPFetcher(
        username="u", password="p", security_token="t", include_opportunities=False
    )
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {"records": MOCK_CONTACTS}
    fetcher._client._sf = mock_sf
    return fetcher


def test_run_returns_documents():
    result = _fetcher_with_mock().run()
    docs = result["documents"]
    assert len(docs) == 1
    assert isinstance(docs[0], Document)


def test_document_content_and_meta():
    docs = _fetcher_with_mock().run()["documents"]
    assert "Jane Smith" in docs[0].content
    assert docs[0].meta["total_gift_amount"] == 50000.0
    assert docs[0].meta["source"] == "salesforce_npsp"


def test_run_override_soql_and_limit():
    fetcher = _fetcher_with_mock()
    fetcher.run(soql_filter="npo02__TotalOppAmount__c > 10000", limit=50)
    soql_used = fetcher._client._sf.query_all.call_args_list[0][0][0]
    assert "npo02__TotalOppAmount__c > 10000" in soql_used
    assert "LIMIT 50" in soql_used


def test_registered_as_component():
    # The @component decorator wires input/output sockets onto instances,
    # so the fetcher can be added to a Haystack pipeline.
    inst = SalesforceNPSPFetcher(username="u", password="p", security_token="t")
    assert hasattr(inst, "__haystack_output__")
    assert "documents" in inst.__haystack_output__._sockets_dict
