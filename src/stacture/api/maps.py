from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Header, Request, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from .base import BaseAPI, LinkType


float_list_pattern = r"^(?:\d+(?:\.\d*)?|\.\d+)(?:,(?:\d+(?:\.\d*)?|\.\d+))*$"


def parse_bbox(
    bbox: Annotated[Optional[str], Query(pattern=float_list_pattern)] = None
) -> Optional[List[float]]:
    if not bbox:
        return None
    bbox = [float(part.strip()) for part in bbox.split(",")]
    if len(bbox) != 4:
        raise RequestValidationError(f"Invalid bounding box size: {len(bbox)}")
    return bbox


class GetMapParameters(BaseModel):
    width: int
    height: int
    bbox: List[float]
    bbox_crs: str


def get_map_common(
    width: int,
    height: int,
    bbox: Annotated[Optional[List[float]], Depends(parse_bbox)] = None,
    bbox_crs: Annotated[Optional[str], Query(alias="bbox-crs")] = None,
    accept: Annotated[str | None, Header()] = None,
) -> GetMapParameters:
    return GetMapParameters(
        width=width, height=height, bbox=bbox, bbox_crs=bbox_crs
    )


GetMapCommon = Annotated[GetMapParameters, Depends(get_map_common)]


router = APIRouter()


@router.get("/map")
def root_map(common: GetMapCommon):
    return {"query": common}


@router.get("/collections/{collection_id}/map")
def collection_map(collection_id: str, common: GetMapCommon):
    return {"collection": collection_id, "query": common}


@router.get("/collections/{collection_id}/styles/{style_id}/map")
def collection_map_styled(
    collection_id: str, style_id: str, common: GetMapCommon
):
    return {"collection": collection_id, "query": common}


MAP_REL = "http://www.opengis.net/def/rel/ogc/1.0/map"


class MapsAPI(BaseAPI):
    def get_api_router(self) -> APIRouter:
        return router

    def get_landing_page_links(self, request: Request) -> List[LinkType]:
        return [
            LinkType(
                href=str(request.url_for("root_map")), rel="abc"
            ).model_dump(exclude_unset=True)
        ]

    def get_collection_links(
        self, request: Request, collection_id: str, collection_conf: dict
    ) -> List[LinkType]:
        map_conf = collection_conf.get("map")
        if map_conf is None:
            return []

        links = [
            LinkType(
                href=str(
                    request.url_for(
                        "collection_map", collection_id=collection_id
                    )
                ),
                rel="http://www.opengis.net/def/rel/ogc/1.0/map",
            ).model_dump(exclude_unset=True)
        ]
        links.extend(
            [
                LinkType(
                    href=str(
                        request.url_for(
                            "collection_map_styled",
                            collection_id=collection_id,
                            style_id=style_id,
                        )
                    ),
                    rel="http://www.opengis.net/def/rel/ogc/1.0/map",
                ).model_dump(exclude_unset=True)
                for style_id in map_conf.get("styles", {}).keys()
            ]
        )
        return links


maps_api = MapsAPI()
