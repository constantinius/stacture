from datetime import datetime
import re
from fastapi import HTTPException, Request, Response

from ows.wms.v13 import encoders as encoders_v13
from ows.wms.types import ServiceCapabilities, Layer, Style

from ows.common.types import (
    OnlineResource, WGS84BoundingBox, BoundingBox,
    ServiceCapabilities as CommonServiceCapabilities,
    Operation as CommonOperation, OperationMethod, HttpMethod
)
from ows.wms.v13.decoders import kvp_decode_getmap, GetMapRequest

from ..source.base import BBox, Query
from ..source.util import get_source

from .base import BaseOWS, service, request, Version


# @service(
#     "wms",
#     versions={
#         # Version(1, 0, 0),
#         # Version(1, 1, 0),
#         # Version(1, 1, 1),
#         Version(1, 3, 0),
#     },
# )
class WebMapService(BaseOWS):
    # @request("GetCapabilities", default_version=Version(1, 3, 0))
    async def get_capabilities(
        self, request: Request, config: dict
    ) -> Response:
        layers = []

        for collection_id, collection_conf in config["collections"].items():
            map_conf = collection_conf.get("map")
            if map_conf is None:
                continue

            source = get_source(collection_conf["source"])
            # TODO: parallelize this here
            collection = await source.get_collection()

            styles = []
            for style_name, style_def in map_conf.get("styles", {}).items():
                styles.append(
                    Style(style_name, style_name, "")
                )
            layers.append(
                Layer(
                    title=collection_conf.get("title", collection.title),
                    name=collection_id,
                    abstract=collection_conf.get(
                        "description", collection.description
                    ),
                    keywords=collection_conf.get(
                        "keywords", collection.keywords
                    ),
                    wgs84_bounding_box=WGS84BoundingBox(collection_conf.get(
                        "extent", collection.extent.spatial.bboxes[0]
                    )),
                    # TODO: dimensions
                    # TODO: styles
                    styles=styles,
                )
            )

        capabilities = ServiceCapabilities.with_defaults(
            str(request.url.replace(query=None)),
            ["image/png", "image/jpeg"],
            layer=Layer(
                title="stacture root",
                name="root",
                abstract="",
                keywords=[],
                crss=[],
                wgs84_bounding_box=[],
                bounding_boxes=[],
                dimensions=[],
                attribution="",
                authority_urls={},
                identifiers={},
                metadata_urls=[],
                data_urls=[],
                feature_list_urls=[],
                styles=[],
                min_scale_denominator=None,
                max_scale_denominator=None,
                layers=layers,
                queryable=True,
                cascaded=None,
                opaque=False,
            ),
        )
        result = encoders_v13.xml_encode_capabilities(capabilities)
        return Response(result.value, media_type=result.content_type)

    @request("GetMap")
    async def get_map(self, request: Request, config: dict) -> Response:
        raw_params = dict(request.query_params)
        raw_params["STYLES"] = "default"
        params: GetMapRequest = kvp_decode_getmap(raw_params.items())
        collection_id = params.layers[0]

        if collection_id in config["collections"]:
            collection_conf = config["collections"][collection_id]
            used_collection = collection_id
        else:
            for used_collection, collection_conf in config["collections"].items():
                if any(
                    re.match(pattern, collection_id)
                    for pattern in collection_conf.get("id_patterns", [])
                ):
                    break
            else:
                raise HTTPException(status_code=404, detail="Item not found")

        source = get_source(collection_conf["source"])

        items = source.search_items(
            Query(
                BBox(*params.bbox, crs=params.crs),
                time=(datetime(2023, 10, 25), datetime(2023, 10, 26)),
                limit=10
            )
        )
        async for item in items:
            print(item.geometry)

