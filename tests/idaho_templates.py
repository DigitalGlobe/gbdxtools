idaho_read = {
    "edges": [],
    "nodes": [
        {
            "id": "IdahoRead",
            "operator": "IdahoRead",
            "parameters": {
                "bucketName": "${bucketName}",
                "imageId": "${imageId}",
                "objectStore": "${objectStore}",
                "targetGSD": "${targetGSD}"
            }
        }
    ]
}

idaho_read_crop_and_format = {
    "edges": [
        {
            "id": "edge-2",
            "index": 1,
            "source": "GeospatialCrop",
            "destination": "Reproject"
        },
        {
            "id": "edge-1",
            "index": 1,
            "source": "IdahoRead",
            "destination": "GeospatialCrop"
        }
    ],
    "nodes": [
        {
            "id": "Reproject",
            "operator": "Reproject",
            "parameters": {
                "Dest SRS Code": "${DestSRSCode:-EPSG:4326}",
                "Dest pixel-to-world transform": "null",
                "Source SRS Code": "${SourceSRSCode:-EPSG:4326}",
                "Source pixel-to-world transform": "null"
            }
        },
        {
            "id": "GeospatialCrop",
            "operator": "GeospatialCrop",
            "parameters": {
                "geospatialWKT": "${geospatialWKT}"
            }
        },
        {
            "id": "IdahoRead",
            "operator": "IdahoRead",
            "parameters": {
                "bucketName": "${bucketName}",
                "imageId": "${imageId}",
                "objectStore": "${objectStore}",
                "targetGSD": "${targetGSD:-}"
            }
        }
    ]
}