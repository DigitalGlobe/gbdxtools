Radarsat = {
    "defaultNodeId": "RadarsatRead",
    "edges": [
        {
            "id": "edge-1",
            "index": 1,
            "source": "RadarsatRead",
            "destination": "Orthorectify"
        }
    ],
    "nodes": [
        {
            "id": "Orthorectify",
            "operator": "Orthorectify",
            "parameters": {
                "Elevation Source": "",
                "Output Coordinate Reference System": "${Output Coordinate Reference System}",
                "Output Pixel to World Transform": "",
                "Sensor Model": "null"
            }
        },
        {
            "id": "RadarsatRead",
            "operator": "RadarsatRead",
            "parameters": {
                "path": "${path}"
            }
        }
    ]
}
