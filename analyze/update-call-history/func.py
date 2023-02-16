import oci
import os
import io
import logging
import json

def handler(ctx, data: io.BytesIO = None):
    
    signer = oci.auth.signers.get_resource_principals_signer()
    object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    
    event = json.loads(data.getvalue())
    object_name = event['data']['resourceName']
    s1 = os.path.basename(object_name)
    s2, _ = os.path.splitext(s1)
    s3, _ = os.path.splitext(s2)
    tpc = s3
    namespace_name = os.environ.get('NAMESPACE_NAME')
    bucket_name = os.environ.get('BUCKET_NAME')

    if not object_name.endswith("wav_AnalyzeResult.json"):
        return

    # Get the contents of the source file
    source_file = object_storage_client.get_object(namespace_name, bucket_name, object_name).data.content
    source_file_stractured = json.loads(source_file)
    logging.getLogger().info(source_file_stractured)
    category = source_file_stractured['textClassificationResult']['documents']
    if not category:
        category = "No conversation exists."
    else:
        category = category[0]['textClassification'][0]['label']
    transcription = source_file_stractured['originalTexts'][0]['text']
    if not transcription:
        transcription = "No conversation exists."
    logging.getLogger().info(category)
    logging.getLogger().info(transcription)


    try:
        # response = update_call_history(signer, tpc, transcription, category)
        response = insert_in_table(signer, tpc, transcription, category)
        logging.getLogger().info(response)

    except Exception as e:
        logging.getLogger().info(e)

def insert_in_table(signer, tpc, transcription, category):
    table_ocid = os.getenv("TABLE_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)

    response = nosql_client.get_row(
        table_name_or_id=table_ocid,
        key=[f"tpc:{tpc}"],
        compartment_id=os.getenv("COMPARTMENT_OCID")
    )

    response = nosql_client.update_row(
        table_name_or_id=table_ocid,
        update_row_details=oci.nosql.models.UpdateRowDetails(
            value={
                'tpc': f"{tpc}",
                'caller': response.data.value['caller'],
                'catcher': response.data.value['catcher'],
                'callStart': response.data.value['callStart'],
                'callEnd': response.data.value['callEnd'],
                'transcription': f"{transcription}",
                'category': f"{category}",
            }
        )
    )

    return response.data
