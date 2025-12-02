"""Universal Data Integration Hub - v4.2 P0"""

from .integration_hub import UniversalDataHub
from .connectors.crm_connector import CRMConnector
from .mapping.auto_mapper import AutoMapper

__all__ = [
    'UniversalDataHub',
    'CRMConnector',
    'AutoMapper',
]
