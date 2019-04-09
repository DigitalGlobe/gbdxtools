worldview_default = {
    "edges": [
        {
            "id": "edge-1",
            "index": 1,
            "source": "DigitalGlobeStrip",
            "destination": "Format"
        },
        {
            "id": "edge-2",
            "index": 1,
            "source": "DigitalGlobeStrip",
            "destination": "RadiometricDRA"
        }
    ],
    "nodes": [
        {
            "id": "Format",
            "operator": "Format",
            "parameters": {
                "dataType": "${dataType}"
            }
        },
        {
            "id": "DigitalGlobeStrip",
            "operator": "DigitalGlobeStrip",
            "parameters": {
                "CRS": "${crs}",
                "GSD": "${gsd}",
                "bands": "${bands}",
                "catId": "${catId}",
                "correctionType": "${correctionType}",
                "fallbackToTOA": "${fallbackToTOA}"
            }
        },
        {
            "id": "RadiometricDRA",
            "operator": "RadiometricDRA",
            "parameters": {}
        }
    ],
    "defaultNodeId": "Format"
}
