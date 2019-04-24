Sentinel2 = {
    "defaultNodeId": "Reproject",
    "edges": [{
        "destination": "Reproject",
        "id": "edge-1",
        "index": 1,
        "source": "Sentinel2Read"
    }],
    "nodes": [{
        "id": "Reproject",
        "operator": "Reproject",
        "parameters": {
            "Dest SRS Code": "${DestSRSCode}",
            "Dest pixel-to-world transform": "null",
            "Source SRS Code": "${SourceSRSCode}",
            "Source pixel-to-world transform": "null"
        }
    },
        {
            "id": "Sentinel2Read",
            "operator": "Sentinel2Read",
            "parameters": {
                "SentinelId": "${sentinelId}",
                "sentinelProductSpec": "${sentinelProductSpec}"
            }
        }
    ]
}

Sentinel1 = {
    "defaultNodeId": "Reproject",
    "edges": [{
        "destination": "Reproject",
        "id": "edge-1",
        "index": 1,
        "source": "Sentinel1Read"
    }],
    "nodes": [{
        "id": "Reproject",
        "operator": "Reproject",
        "parameters": {
            "Dest SRS Code": "${DestSRSCode}",
            "Dest pixel-to-world transform": "null",
            "Source SRS Code": "${SourceSRSCode}",
            "Source pixel-to-world transform": "null"
        }
    },
        {
            "id": "Sentinel1Read",
            "operator": "Sentinel1Read",
            "parameters": {
                "SentinelId": "${sentinelId}",
                "sentinel1Polarization": "${sentinel1Polarization}"
            }
        }
    ]
}

