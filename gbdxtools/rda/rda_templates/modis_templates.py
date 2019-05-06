Modis = {
    "defaultNodeId": "ModisRead",
    "edges": [
        {
            "id": "edge-1",
            "index": 1,
            "source": "ModisRead",
            "destination": "Reproject"
        }
    ],
    "nodes": [
        {
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
            "id": "ModisRead",
            "operator": "ModisRead",
            "parameters": {
                "modisId": "${modisId}"
            }
        }
    ]
}
