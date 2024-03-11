from typing import Annotated
from fastapi import APIRouter, Depends, Request

from ..config import get_config
from .wms import WebMapService


Config = Annotated[dict, Depends(get_config)]
router = APIRouter()




wms = WebMapService()


@router.get("/ows")
async def ows_get(request: Request, config: Config):

    query = {
        key.lower(): value
        for key, value in request.query_params.items()
    }
    if query.get("service").upper() == "WMS":
        pass
        if query.get("request").upper() == "GetCapabilities".upper():

            return await wms.get_capabilities(request, config)

        elif query.get("request").upper() == "GetMap".upper():
            return await wms.get_map(request, config)
