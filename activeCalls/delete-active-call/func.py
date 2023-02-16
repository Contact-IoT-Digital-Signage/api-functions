import io
import json
import os
import oci
from fdk import response
from dotenv import load_dotenv


'''
    This function deletes an active call by call ID(tpc)
'''
def handler(ctx, data: io.BytesIO = None):
    load_dotenv()
    try:
        request_body = json.loads(data.getvalue())
        tpc = request_body.get("tpc")
    except Exception:
        msg = "tpc not found in request body"
        return response.Response(ctx, msg, status_code = 400)
        
    signer = oci.auth.signers.get_resource_principals_signer()
    delete_call(signer, tpc)

def delete_call(signer, call_id):

    table_ocid = os.getenv("TABLE_OCID")
    compartment_ocid = os.getenv("COMPARTMENT_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)

    nosql_client.delete_row(
        table_name_or_id=table_ocid,
        key=[f"tpc:{call_id}"],
        compartment_id=compartment_ocid
    )
    