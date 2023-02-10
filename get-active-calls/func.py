import io
import json
from fdk import response
import io
import json
import oci
import os
from dotenv import load_dotenv

def handler(ctx, data: io.BytesIO = None):
    load_dotenv()
    signer = oci.auth.signers.get_resource_principals_signer()
    get_active_tokens(signer)

def get_active_tokens(signer):
    
    compartment_ocid = os.getenv("COMPARTMENT_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)

    get_active_calls_statement = \
        'select * from zoomtokens where isActive = true'

    prepare_statement_response = \
        nosql_client.prepare_statement(compartment_id=compartment_ocid,statement=get_active_calls_statement)
    
    print(prepare_statement_response.data.statement, flush=True)

    query_response = nosql_client.query(
        query_details=oci.nosql.models.QueryDetails(
            compartment_id=compartment_ocid,
            statement=prepare_statement_response,
            is_prepared=True,
            consistency="EVENTUAL"
        )
    )

    print(query_response.data, flush=True)