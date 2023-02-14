import io
import json
import os
import oci
import logging
from fdk import response
from dotenv import load_dotenv


def handler(ctx, data: io.BytesIO = None):
    load_dotenv()
    try:
        request_body = json.loads(data.getvalue())
        tpc = request_body.get("tpc")
    except(Exception) as ex:
        msg = "tpc not found in request body"
        logging.getLogger().info(str(ex))
        return response.Response(ctx, msg, status_code = 400)
        
    signer = oci.auth.signers.get_resource_principals_signer()
    db_response_data = delete_call(signer, tpc)

    print(db_response_data, flush=True)

def delete_call(signer, call_id):

    table_ocid = os.getenv("TABLE_OCID")
    compartment_ocid = os.getenv("COMPARTMENT_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)

    delete_row_response = nosql_client.delete_row(
        table_name_or_id=table_ocid,
        key=[f"tpc:{call_id}"],
        compartment_id=compartment_ocid
    )

    return delete_row_response.data