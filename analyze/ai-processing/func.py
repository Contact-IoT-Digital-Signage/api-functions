import oci
import os
import io
import logging
import json
import datetime

def handler(ctx, data: io.BytesIO = None):
    event = json.loads(data.getvalue())
    object_name = event['data']['resourceName']
    object_file_name = object_name.split('.')[0] 

    signer = oci.auth.signers.get_resource_principals_signer()
    media_flow = oci.media_services.MediaServicesClient({}, signer=signer)

    compartment_id = os.environ.get('COMPARTMENT_ID')
    media_workflow_id = os.environ.get('MEDIA_WORKFLOW_ID')
    
    job_details = oci.media_services.models.CreateMediaWorkflowJobByIdDetails(
        compartment_id=compartment_id,
        workflow_identifier_type=oci.media_services.models.CreateMediaWorkflowJobDetails.WORKFLOW_IDENTIFIER_TYPE_ID,
        media_workflow_id=media_workflow_id,
        display_name=object_file_name,
        parameters={
            "input": {
                "objectName": object_name,
                "objectNameFilename": object_file_name
            },
        }
    )
    try:
        response = media_flow.create_media_workflow_job(job_details)
        logging.getLogger().info(response)

    except Exception as e:
        logging.getLogger().info(e)