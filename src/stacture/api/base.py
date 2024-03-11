from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel


class LinkType(BaseModel):
    href: str
    rel: str
    type: Optional[str] = None
    hreflang: Optional[str] = None
    title: Optional[str] = None
    length: Optional[int] = None


class BaseAPI(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_api_router(self) -> APIRouter:
        ...

    @abstractmethod
    def get_landing_page_links(self, request: Request) -> List[LinkType]:
        ...

    @abstractmethod
    def get_collection_links(self, request: Request, collection_id: str, collection_conf: dict) -> List[LinkType]:
        ...
