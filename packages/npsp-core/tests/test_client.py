"""Tests for SalesforceNPSPClient. All mock simple_salesforce — no creds."""

from unittest.mock import MagicMock

import pytest

from npsp_core import SalesforceNPSPClient

MOCK_CONTACTS = [
    {
        "Id": "003XXXXXXXXXXXXXXX",
        "FirstName": "Jane",
        "LastName": "Smith",
        "Email": "jane@example.org",
        "Title": None,
        "npo02__TotalOppAmount__c": 50000.0,
        "npo02__NumberOfClosedOpps__c": 5.0,
        "npo02__LastCloseDate__c": "2024-02-15",
        "npo02__FirstCloseDate__c": "2018-06-01",
        "npo02__AverageAmount__c": 10000.0,
        "npo02__LargestAmount__c": 25000.0,
        "npo02__LastMembershipDate__c": None,
        "npsp__Primary_Affiliation__r": {"Name": "City Hospital"},
        "npsp__Soft_Credit_Total__c": 5000.0,
        "npsp__Planned_Giving_Count__c": 1.0,
        "LastActivityDate": "2023-08-01",
        "CreatedDate": "2018-05-15T10:00:00.000+0000",
    }
]

MOCK_OPPORTUNITIES = [
    {
        "Id": "006XXXXXXXXXXXXXXX",
        "Name": "Jane Smith Major Gift",
        "Amount": 25000.0,
        "CloseDate": "2024-02-15",
        "StageName": "Closed Won",
        "RecordType": {"Name": "Major Gift"},
        "npsp__Acknowledgment_Status__c": "Acknowledged",
        "npsp__Gift_Strategy__c": "Major Gift",
        "Primary_Contact__c": "003XXXXXXXXXXXXXXX",
    }
]


@pytest.fixture
def mock_sf():
    sf = MagicMock()
    sf.query_all.side_effect = [
        {"records": MOCK_CONTACTS},
        {"records": MOCK_OPPORTUNITIES},
    ]
    return sf


@pytest.fixture
def client():
    return SalesforceNPSPClient(
        username="test@example.org",
        password="password",
        security_token="TOKEN",
        domain="test",
    )


def test_init_from_args():
    c = SalesforceNPSPClient(username="u", password="p", security_token="t")
    assert c.username == "u"
    assert c.include_opportunities is True


def test_init_from_env(monkeypatch):
    monkeypatch.setenv("SF_USERNAME", "env_user")
    monkeypatch.setenv("SF_PASSWORD", "env_pass")
    monkeypatch.setenv("SF_TOKEN", "env_token")
    c = SalesforceNPSPClient()
    assert c.username == "env_user"


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("SF_USERNAME", raising=False)
    monkeypatch.delenv("SF_PASSWORD", raising=False)
    monkeypatch.delenv("SF_TOKEN", raising=False)
    with pytest.raises(ValueError, match="credentials"):
        SalesforceNPSPClient()


def test_load_donors_returns_records(client, mock_sf):
    client._sf = mock_sf
    recs = client.load_donors()
    assert isinstance(recs, list)
    assert len(recs) == 1
    assert set(recs[0].keys()) == {"text", "metadata"}


def test_text_contains_donor_name(client, mock_sf):
    client._sf = mock_sf
    recs = client.load_donors()
    assert "Jane Smith" in recs[0]["text"]


def test_text_contains_gift_history(client, mock_sf):
    client._sf = mock_sf
    recs = client.load_donors()
    assert "$25,000" in recs[0]["text"]


def test_metadata_keys(client, mock_sf):
    client._sf = mock_sf
    recs = client.load_donors()
    expected = {
        "donor_id",
        "donor_name",
        "email",
        "affiliation",
        "total_gift_amount",
        "gift_count",
        "average_gift_amount",
        "largest_gift_amount",
        "first_gift_date",
        "last_gift_date",
        "last_activity_date",
        "soft_credit_total",
        "planned_giving_count",
        "source",
    }
    assert expected == set(recs[0]["metadata"].keys())


def test_metadata_values(client, mock_sf):
    client._sf = mock_sf
    recs = client.load_donors()
    m = recs[0]["metadata"]
    assert m["total_gift_amount"] == 50000.0
    assert m["gift_count"] == 5
    assert m["source"] == "salesforce_npsp"


def test_affinity_score_injected(mock_sf):
    client = SalesforceNPSPClient(
        username="u", password="p", security_token="t",
        affinity_score_fn=lambda meta: 87.5,
    )
    mock_sf.query_all.side_effect = [
        {"records": MOCK_CONTACTS},
        {"records": MOCK_OPPORTUNITIES},
    ]
    client._sf = mock_sf
    recs = client.load_donors()
    assert recs[0]["metadata"]["affinity_score"] == 87.5


def test_affinity_score_exception_handled(mock_sf):
    def bad_scorer(meta):
        raise RuntimeError("model not fitted")

    client = SalesforceNPSPClient(
        username="u", password="p", security_token="t",
        affinity_score_fn=bad_scorer,
    )
    mock_sf.query_all.side_effect = [
        {"records": MOCK_CONTACTS},
        {"records": MOCK_OPPORTUNITIES},
    ]
    client._sf = mock_sf
    recs = client.load_donors()
    assert recs[0]["metadata"]["affinity_score"] is None


def test_empty_contacts_returns_empty_list(client):
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {"records": []}
    client._sf = mock_sf
    assert client.load_donors() == []


def test_no_opportunities_mode():
    client = SalesforceNPSPClient(
        username="u", password="p", security_token="t",
        include_opportunities=False,
    )
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {"records": MOCK_CONTACTS}
    client._sf = mock_sf
    client.load_donors()
    assert mock_sf.query_all.call_count == 1


def test_contact_ids_filter(client, mock_sf):
    client._sf = mock_sf
    client.load_donors(contact_ids=["003XXXXXXXXXXXXXXX"])
    soql_used = mock_sf.query_all.call_args_list[0][0][0]
    assert "003XXXXXXXXXXXXXXX" in soql_used


def test_missing_npsp_fields_handled_gracefully(client):
    sparse = {
        "Id": "003YYY",
        "FirstName": None,
        "LastName": None,
        "Email": None,
        "Title": None,
        "npo02__TotalOppAmount__c": None,
        "npo02__NumberOfClosedOpps__c": None,
        "npo02__LastCloseDate__c": None,
        "npo02__FirstCloseDate__c": None,
        "npo02__AverageAmount__c": None,
        "npo02__LargestAmount__c": None,
        "npo02__LastMembershipDate__c": None,
        "npsp__Primary_Affiliation__r": None,
        "npsp__Soft_Credit_Total__c": None,
        "npsp__Planned_Giving_Count__c": None,
        "LastActivityDate": None,
        "CreatedDate": None,
    }
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {"records": [sparse]}
    client._sf = mock_sf
    recs = client.load_donors()
    assert len(recs) == 1
    assert recs[0]["metadata"]["total_gift_amount"] == 0.0


def test_soql_filter_passed_through(client, mock_sf):
    client._sf = mock_sf
    client.load_donors(soql_filter="npo02__TotalOppAmount__c > 10000", limit=50)
    soql_used = mock_sf.query_all.call_args_list[0][0][0]
    assert "npo02__TotalOppAmount__c > 10000" in soql_used
    assert "LIMIT 50" in soql_used


def test_contact_ids_ignores_soql_filter_and_limit(client, mock_sf):
    client._sf = mock_sf
    client.load_donors(
        contact_ids=["003XXXXXXXXXXXXXXX"],
        soql_filter="npo02__TotalOppAmount__c > 99999",
        limit=1,
    )
    soql_used = mock_sf.query_all.call_args_list[0][0][0]
    assert "003XXXXXXXXXXXXXXX" in soql_used
    assert "npo02__TotalOppAmount__c > 99999" not in soql_used
    assert "LIMIT" not in soql_used
