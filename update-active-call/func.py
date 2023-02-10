import io
import json
import logging
import oci
import base64
import os
from fdk import response
from dotenv import load_dotenv


'''
    Function sets the status of a call to active (connected)
'''
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
    activate_token(signer, tpc)

def activate_token(signer, tpc):

    compartment_ocid = os.getenv("COMPARTMENT_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)

    update_statement = \
        'update zoomtokens set isActive = true where tpc = $Tpc and isActive = false'

    prepare_statement_response = \
        nosql_client.prepare_statement(compartment_id=compartment_ocid,statement=update_statement)

    print(prepare_statement_response.data.statement, flush=True)

    query_response = nosql_client.query(
        query_details=oci.nosql.models.QueryDetails(
            compartment_id=compartment_ocid,
            statement=prepare_statement_response.data.statement,
            is_prepared=True,
            consistency="EVENTUAL",
            variables={
                '$Tpc': tpc
            }
        )
    )

    print(query_response.data)