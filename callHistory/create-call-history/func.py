import io
import json
import oci
import os
from dotenv import load_dotenv
from datetime import datetime
from fdk import response


def handler(ctx, data: io.BytesIO = None):

    load_dotenv()

    try:
        request_body = json.loads(data.getvalue())
        tpc = request_body.get("tpc")
        caller = request_body.get("caller")
        catcher = request_body.get("catcher")
        callStart = request_body.get("callStart")
        callEnd = request_body.get("callEnd")
        transcription = request_body.get("transcription")
        category = request_body.get("category")

    except Exception:
        msg = "mandatory field missing in request body"
        return response.Response(ctx, msg, status_code = 400)

    signer = oci.auth.signers.get_resource_principals_signer()
    
    insert_in_table(signer=signer, tpc=tpc, caller=caller, catcher=catcher, callStart=callStart, \
         callEnd=callEnd, transcription=transcription, category=category)
    
    return response.Response(ctx, status_code = 200)


def insert_in_table(signer, tpc, caller, catcher, callStart, callEnd, transcription, category):

    table_ocid = os.getenv("TABLE_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)
    nosql_client.update_row(
        table_name_or_id=table_ocid,
        update_row_details=oci.nosql.models.UpdateRowDetails(
            value={
                'tpc': f'{tpc}',
                'caller': f'{caller}',
                'catcher': f'{catcher}',
                'callStart': f'{datetime.fromtimestamp(callStart).strftime("%Y-%m-%dT%H:%M:%S")}',
                'callEnd': f'{datetime.fromtimestamp(callEnd).strftime("%Y-%m-%dT%H:%M:%S")}',
                'transcription': f'{transcription}',
                'category': f'{category}',
            }
        )
    )