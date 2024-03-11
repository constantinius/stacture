from typing import Optional

from ows.common.types import Version

from .base import BaseOWS


class OWSRegistry:
    def __init__(self):
        self.ows = {}

    def register(self, ows: BaseOWS):
        service_reg = self.ows.setdefault(ows._OWS_SERVICE_NAME.lower(), {})
        for version in ows._OWS_SERVICE_VERSIONS:
            service_reg[version] = ows

    def get_handler(self, service: str, version: Optional[Version], request: str):
        versions = self.ows.get(service)

