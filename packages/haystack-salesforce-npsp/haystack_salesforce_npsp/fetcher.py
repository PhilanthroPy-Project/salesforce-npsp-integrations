"""Haystack component that fetches Salesforce NPSP donors as Documents."""

from typing import Any, Callable, Dict, List, Optional

from haystack import Document, component
from npsp_core import SalesforceNPSPClient


@component
class SalesforceNPSPFetcher:
    """Fetch Salesforce NPSP donor records as Haystack Documents.

    Wraps :class:`npsp_core.SalesforceNPSPClient`. Each donor becomes one
    ``Document`` whose ``content`` is the narrative donor profile and whose
    ``meta`` carries the structured donor fields, ready to index for RAG.

    Credentials fall back to ``SF_USERNAME`` / ``SF_PASSWORD`` / ``SF_TOKEN``
    env vars when not passed explicitly.

    Example:
        >>> from haystack import Pipeline
        >>> from haystack_salesforce_npsp import SalesforceNPSPFetcher
        >>> fetcher = SalesforceNPSPFetcher(soql_filter="npo02__TotalOppAmount__c > 5000")
        >>> docs = fetcher.run()["documents"]
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[str] = None,
        domain: str = "login",
        include_opportunities: bool = True,
        soql_filter: str = "npo02__TotalOppAmount__c > 0",
        limit: int = 500,
        affinity_score_fn: Optional[Callable[[Dict[str, Any]], float]] = None,
    ) -> None:
        self._client = SalesforceNPSPClient(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain,
            include_opportunities=include_opportunities,
            affinity_score_fn=affinity_score_fn,
        )
        self.soql_filter = soql_filter
        self.limit = limit

    @component.output_types(documents=List[Document])
    def run(
        self,
        contact_ids: Optional[List[str]] = None,
        soql_filter: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[Document]]:
        """Fetch donors and return them as Haystack Documents.

        Args:
            contact_ids: Explicit Contact IDs. When set, soql_filter/limit
                are ignored (mirrors the underlying client).
            soql_filter: Override the instance SOQL WHERE clause for this run.
            limit: Override the instance record limit for this run.
        """
        records = self._client.load_donors(
            contact_ids=contact_ids,
            soql_filter=soql_filter if soql_filter is not None else self.soql_filter,
            limit=limit if limit is not None else self.limit,
        )
        documents = [
            Document(content=r["text"], meta=r["metadata"]) for r in records
        ]
        return {"documents": documents}
