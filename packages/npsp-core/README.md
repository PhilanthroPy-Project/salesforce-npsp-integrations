# salesforce-npsp-core

Framework-neutral reader for Salesforce **Nonprofit Success Pack (NPSP)** donor
data. Fetches donor `Contact` records, `Opportunity` gift histories, and NPSP
engagement metrics via [`simple_salesforce`](https://github.com/simple-salesforce/simple-salesforce),
returning one plain `{"text", "metadata"}` record per donor.

This is the shared core behind:

- **[haystack-salesforce-npsp](../haystack-salesforce-npsp)** — Haystack 2.x component
- **[mcp-server-salesforce-npsp](../mcp-server-salesforce-npsp)** — Model Context Protocol server

All Salesforce/SOQL logic lives here, once.

## Usage

```python
from npsp_core import SalesforceNPSPClient

client = SalesforceNPSPClient(domain="login")  # or env: SF_USERNAME/SF_PASSWORD/SF_TOKEN
records = client.load_donors(soql_filter="npo02__TotalOppAmount__c > 5000", limit=500)
# records[0] == {"text": "Donor Profile: ...", "metadata": {"donor_id": ..., ...}}
```

Pass `affinity_score_fn=(metadata) -> float` to inject an ML propensity score
into each record's metadata at load time.
