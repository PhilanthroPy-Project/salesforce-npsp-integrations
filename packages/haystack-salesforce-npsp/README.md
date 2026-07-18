# Haystack — Salesforce NPSP

A [Haystack 2.x](https://haystack.deepset.ai/) component that ingests Salesforce
**Nonprofit Success Pack (NPSP)** donor data as `Document`s for RAG pipelines —
no Airbyte, no CDK.

Unlike a raw Salesforce connector, this is **NPSP-aware**: it understands
`npo02__` and `npsp__` field prefixes and emits human-readable donor summaries
(giving totals, gift history, engagement) instead of raw JSON.

## Installation

```bash
pip install haystack-salesforce-npsp
```

## Credentials

```bash
export SF_USERNAME="you@yourorg.org"
export SF_PASSWORD="your_password"
export SF_TOKEN="your_security_token"
```

## Usage

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_salesforce_npsp import SalesforceNPSPFetcher

store = InMemoryDocumentStore()

indexing = Pipeline()
indexing.add_component("fetch", SalesforceNPSPFetcher(
    soql_filter="npo02__TotalOppAmount__c > 5000",
    limit=500,
))
indexing.add_component("embed", SentenceTransformersDocumentEmbedder())
indexing.add_component("write", DocumentWriter(document_store=store))
indexing.connect("fetch.documents", "embed.documents")
indexing.connect("embed.documents", "write.documents")

indexing.run({})
```

Each `Document` has:

- `.content` — narrative donor profile (name, giving summary, recent gifts)
- `.meta` — structured donor fields (`donor_id`, `total_gift_amount`,
  `gift_count`, `affiliation`, `source="salesforce_npsp"`, …)

### Affinity scores

Pass a callable `(meta: dict) -> float` as `affinity_score_fn` to inject an
ML-derived donor propensity score into every document's metadata at fetch time.

```python
SalesforceNPSPFetcher(affinity_score_fn=lambda m: min(50 + m["total_gift_amount"] / 5000, 100))
```

> **Note:** because `affinity_score_fn` is an arbitrary callable, a fetcher
> configured with one is not YAML-serializable. Instantiate it in Python.
