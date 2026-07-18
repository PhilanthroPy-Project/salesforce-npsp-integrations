# Salesforce NPSP Integrations

NPSP-aware Salesforce donor readers for the AI ecosystem. One shared core, two
adapters — repurposed from a LlamaIndex reader into the frameworks that are
actually accepting net-new integrations.

Part of the **[PhilanthroPy](https://github.com/PhilanthroPy-Project/PhilanthroPy)**
donor-analytics ecosystem — this repo is the data on-ramp that pulls Salesforce
Nonprofit Success Pack records into RAG pipelines and agent tools.

## Packages

| Package | What it is | Distribution |
| --- | --- | --- |
| [`salesforce-npsp-core`](packages/npsp-core) | Framework-neutral Salesforce/SOQL logic → `{"text","metadata"}` donor records | PyPI |
| [`haystack-salesforce-npsp`](packages/haystack-salesforce-npsp) | Haystack 2.x component → `Document`s | PyPI + `haystack-integrations` PR |
| [`mcp-server-salesforce-npsp`](packages/mcp-server-salesforce-npsp) | MCP server → tools for any MCP client | PyPI + MCP Registry |

`salesforce-npsp-core` holds all the Salesforce/SOQL logic; the Haystack
component and the MCP server are thin wrappers over it, so the connector code
lives in exactly one place.

## Ecosystem

These readers are one half of the [PhilanthroPy](https://github.com/PhilanthroPy-Project)
stack for nonprofit donor analytics:

- **[PhilanthroPy](https://github.com/PhilanthroPy-Project/PhilanthroPy)** — an
  sklearn-native donor-propensity / analytics library. Plug a fitted model into
  this repo's `affinity_score_fn` to score donors at ingest time.
- **[UniSchema](https://github.com/PhilanthroPy-Project/UniSchema)** — a
  TypeScript/npm webhook normalizer that emits a canonical `ConstituentEvent`
  stream from fundraising sources.
- **salesforce-npsp-integrations** (this repo) — ingests NPSP donor data
  directly from Salesforce into Haystack (RAG) and MCP (agent tools).

## Why NPSP-aware?

Generic Salesforce connectors emit raw JSON. These understand the Nonprofit
Success Pack schema (`npo02__`, `npsp__`) and produce human-readable donor
profiles — giving totals, gift history, engagement — that an LLM can reason
over directly. Optional `affinity_score_fn` injects an ML propensity score per
donor.

## Develop

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e packages/npsp-core[test] \
            -e packages/haystack-salesforce-npsp[test] \
            -e packages/mcp-server-salesforce-npsp[test]
pytest packages
```

## Publish order

`salesforce-npsp-core` first (the adapters depend on it), then the two adapters.
