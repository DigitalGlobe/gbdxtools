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
                "Dest SRS Code": "${Dest SRS Code}",
                "Dest pixel-to-world transform": "null",
                "Source SRS Code": "${Source SRS Code}",
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
