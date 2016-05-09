from gbdxtools import Interface

"""
Example using batch workflow endpoint to create multiple workflows with 1 submission
"""

batch_workflow_json = {
    "name": "fastortho_stagetos3",
    "batch_values": [
        {
            "name": "input_data",
            "values": [
                "http://test-tdgplatform-com/temp/1",
                "http://test-tdgplatform-com/temp/2",
                "http://test-tdgplatform-com/temp/3"
            ]
        },
        {
            "name": "input_dem",
            "values": [
                "SRTM90",
                "SRTM120",
                "SRTM150"
            ]
        },
        {
            "name": "destination",
            "values": [
                "http://test-tdgplatform-com/temp/1",
                "http://test-tdgplatform-com/temp/2",
                "http://test-tdgplatform-com/temp/3"
            ]
        }
    ],
    "tasks": [
        {
            "name": "FastOrtho",
            "outputs": [
                {
                    "name": "data"
                }
            ],
            "inputs": [
                {
                    "name": "data",
                    "value": "$batch_value:input_data"
                },
                {
                    "name": "demspecifier",
                    "value": "$batch_value:input_dem"
                }
            ],
            "taskType": "FastOrtho"
        },
        {
            "name": "StagetoS3",
            "inputs": [
                {
                    "name": "data",
                    "source": "FastOrtho:data"
                },
                {
                    "name": "destination",
                    "value": "$batch_value:destination"
                }
            ],
            "taskType": "StageDataToS3"
        }
    ]
}


def go():
    # create batch workflow
    batch_workflow_id = gbdx.workflow.launch_batch_workflow(batch_workflow_json)
    # check status
    print gbdx.workflow.batch_workflow_status(batch_workflow_id)
    # cancel batch workflow
    print gbdx.workflow.batch_workflow_cancel(batch_workflow_id)

if __name__ == "__main__":
    gbdx = Interface()
    go()
