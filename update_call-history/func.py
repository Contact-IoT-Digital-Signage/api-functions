import oci
import os
import io
import logging
import json

def handler(ctx, data: io.BytesIO = None):
    
    signer = oci.auth.signers.get_resource_principals_signer()
    object_storage_client = oci.object_storage.ObjectStorageClient({}, signer)
    
    event = json.loads(data.getvalue())
    object_name = event['data']['resourceName']
    bucket_name = os.environ.get('BUCKET_NAME')
    logging.getLogger().info(object_name)

    # Get the contents of the source file
    source_file = object_storage_client.get_object(
        bucket_name, object_name).data.content
    logging.getLogger().info(source_file)
    transcription = source_file['']
    category = source_file['']

    try:
        response = insert_call_history(signer, transcription, category)
        logging.getLogger().info(response)

    except Exception as e:
        logging.getLogger().info(e)

def insert_call_history(signer, transcription, category):

    table_ocid = os.environ.get("TABLE_OCID")
    nosql_client = oci.nosql.NosqlClient({}, signer=signer)
    nosql_client.update_row(
        table_name_or_id=table_ocid,
        update_row_details=oci.nosql.models.UpdateRowDetails(
            value={
                'transcription': f"{transcription}",
                'category': f"{category}"
            }
        )
    )
    