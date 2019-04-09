digital_globe_strip = {
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

digital_globe_image = {
    "defaultNodeId": "DigitalGlobeImage",
    "edges": [],
    "nodes": [
        {
            "id": "DigitalGlobeImage",
            "operator": "DigitalGlobeImage",
            "parameters": {
                "bucketName": "${bucketName}",
                "imageId": "${imageId}",
                "CRS": "${CRS}",
                "correctionType": "${correctionType}",
                "GSD": "${GSD}",
                "fallbackToTOA": "true",
                "bands": "${bands}"
            }
        }
    ]
}
