Ikonos = {
    "edges": [
        {
            "id": "edge-1",
            "index": 1,
            "source": "IkonosRead",
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
            "id": "IkonosRead",
            "operator": "IkonosRead",
            "parameters": {
                "path": "${path}",
            }
        }
    ]
}

IkonosPanSharpen = {
    "defaultNodeId": "LocallyProjectivePanSharpen",
    "edges": [
        {
            "id": "edge-4",
            "index": 1,
            "source": "OrthorectifyMulti",
            "destination": "LocallyProjectivePanSharpen"
        },
        {
            "id": "edge-3",
            "index": 2,
            "source": "OrthorectifyPan",
            "destination": "LocallyProjectivePanSharpen"
        },
        {
            "id": "edge-2",
            "index": 1,
            "source": "IkonosReadMulti",
            "destination": "OrthorectifyMulti"
        },
        {
            "id": "edge-1",
            "index": 1,
            "source": "IkonosReadPan",
            "destination": "OrthorectifyPan"
        }
    ],
    "nodes": [
        {
            "id": "LocallyProjectivePanSharpen",
            "operator": "LocallyProjectivePanSharpen",
            "parameters": {}
        },
        {
            "id": "OrthorectifyMulti",
            "operator": "Orthorectify",
            "parameters": {
                "Elevation Source": "",
                "Output Coordinate Reference System": "${Output Coordinate Reference System}",
                "Output Pixel to World Transform": "",
                "Sensor Model": "null"
            }
        },
        {
            "id": "IkonosReadMulti",
            "operator": "IkonosRead",
            "parameters": {
                "path": "${multiPath}",
            }
        },
        {
            "id": "OrthorectifyPan",
            "operator": "Orthorectify",
            "parameters": {
                "Elevation Source": "",
                "Output Coordinate Reference System": "${Output Coordinate Reference System}",
                "Output Pixel to World Transform": "",
                "Sensor Model": "null"
            }
        },
        {
            "id": "IkonosReadPan",
            "operator": "IkonosRead",
            "parameters": {
                "path": "${panPath}",
                "productSpec": "panchromatic"
            }
        }
    ]
}
