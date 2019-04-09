landsat_pansharp = {
    "edges": [
        {
            "id": "edge-2",
            "index": 2,
            "source": "LandsatReadPanchromatic",
            "destination": "LocallyProjectivePanSharpen"
        },
        {
            "id": "edge-1",
            "index": 1,
            "source": "LandsatReadMultispectral",
            "destination": "LocallyProjectivePanSharpen"
        },
        {
            "id": "edge-3",
            "index": 1,
            "source": "LocallyProjectivePanSharpen",
            "destination": "Reproject"
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
            "id": "LocallyProjectivePanSharpen",
            "operator": "LocallyProjectivePanSharpen",
            "parameters": {}
        },
        {
            "id": "LandsatReadMultispectral",
            "operator": "LandsatRead",
            "parameters": {
                "landsatId": "${catalogIdMultispectral}",
                "productSpec": "multispectral"
            }
        },
        {
            "id": "LandsatReadPanchromatic",
            "operator": "LandsatRead",
            "parameters": {
                "landsatId": "${catalogIdPanchromatic}",
                "productSpec": "panchromatic"
            }
        }
    ],
    "defaultNodeId": "LocallyProjectivePanSharpen"
}

landsat_proj = {
    "defaultNodeId": "LandsatRead",
    "edges": [{
        "destination": "Reproject",
        "id": "edge-1",
        "index": 1,
        "source": "LandsatRead"
    }],
    "nodes": [{
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
            "id": "LandsatRead",
            "operator": "LandsatRead",
            "parameters": {
                "landsatId": "${catalogId}",
                "productSpec": "${productSpec}"
            }
        }
    ]
}
