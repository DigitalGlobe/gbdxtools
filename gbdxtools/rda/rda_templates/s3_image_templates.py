S3Image = {
    "defaultNodeId": "GdalImageRead",
    "edges": [
        {
            "destination": "Reproject",
            "id": "edge-1",
            "index": 1,
            "source": "GdalImageRead"
        }
    ],
    "nodes": [
        {
            "id": "Reproject",
            "operator": "Reproject",
            "parameters": {
                "Dest pixel-to-world transform": "",
                "Resampling Kernel": "INTERP_BILINEAR",
                "Source SRS Code": "${SourceSRSCode}",
                "Source pixel-to-world transform": "",
                "Dest SRS Code": "${DestSRSCode}",
                "Background Values": "[0]"
            }
        },
        {
            "id": "GdalImageRead",
            "operator": "GdalImageRead",
            "parameters": {
                "path": "${path}"
            }
        }
    ]
}
