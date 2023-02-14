import oci
import os
import io
import logging
import json
import datetime

def handler(ctx, data: io.BytesIO = None):
    event = json.loads(data.getvalue())
    object_name = event['data']['resourceName']

    signer = oci.auth.signers.get_resource_principals_signer()
    media_flow = oci.media_services.MediaServicesClient({}, signer=signer)

    media_workflow_id = os.environ.get('MEDIA_WORKFLOW_ID')
    compartment_id = os.environ.get('COMPARTMENT_ID')
    date = datetime.datetime.now().strftime("%m-%d-%Y_%H%M")

    sample = media_flow.list_media_workflow_configurations(compartment_id=compartment_id)
    #logging.getLogger().info(sample.data.items)

    job_details = oci.media_services.models.CreateMediaWorkflowJobByIdDetails(
        compartment_id=compartment_id,
        workflow_identifier_type=oci.media_services.models.CreateMediaWorkflowJobDetails.WORKFLOW_IDENTIFIER_TYPE_ID,
        media_workflow_id=media_workflow_id,
        parameters={
            "input": {
                "objectName": object_name,
                "objectNameFilename": object_name
            },
            #TODO: remove duplicates of output file name
            # "output":{
            #     "objectNameFilename": object_name+date,
            # } 
        }
    )
    try:
        response = media_flow.create_media_workflow_job(job_details)
        logging.getLogger().info(response)

    except Exception as e:
        logging.getLogger().info(e)

