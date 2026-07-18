"""Framework-neutral Salesforce NPSP client shared by all adapters."""

from npsp_core.client import DonorRecord, SalesforceNPSPClient

__all__ = ["SalesforceNPSPClient", "DonorRecord"]
