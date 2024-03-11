from typing import Annotated, List

from fastapi import FastAPI, APIRouter, Depends, Request, Query
from pydantic import BaseModel

from stacture.source.stac_api import STACAPISource

from .settings import get_settings
from .source.base import Query as SourceQuery


from .api import get_registry
from .ows.router import router as ows_router
from .config import get_config

app = FastAPI()


api_registry = get_registry()

for api in api_registry.apis:
    app.include_router(api.get_api_router())


app.include_router(ows_router)
