import io
import json
import logging
from fdk import response
import oci
import base64
import os
from dotenv import load_dotenv
import time
import jwt


def handler(ctx, data: io.BytesIO = None):

    load_dotenv()
    zoom_secret_ocid = os.getenv("ZOOM_SECRET_OCID")

    try:
        request_body = json.loads(data.getvalue())
        tpc = request_body.get("tpc")

    except(Exception) as ex:
        msg = "tpc not found in request body"
        logging.getLogger().info(str(ex))
        return response.Response(ctx, msg, status_code = 400)

    signer = oci.auth.signers.get_resource_principals_signer()
    zoom_sdk_key = get_secret(signer, zoom_secret_ocid)

    zoom_tokens = get_zoom_tokens(tpc, zoom_sdk_key)
    insert_in_table(signer, tpc, zoom_tokens[1])
    
    return response.Response(
        ctx, response_data=json.dumps(
            {"token": f"{zoom_tokens[0]}"}),
        headers={"Content-Type": "application/json"}
    )

# Retrieve secret
def get_secret(signer, secret_ocid):
    
    secret_client = oci.secrets.SecretsClient({}, signer=signer)    
    secret = secret_client.get_secret_bundle(secret_ocid).data.secret_bundle_content.content.encode('utf-8')
    decrypted_secret = base64.b64decode(secret).decode("utf-8")
    return decrypted_secret

def insert_in_table(signer, tpc, token):

    table_ocid = os.getenv("TABLE_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)
    nosql_client.update_row(
        table_name_or_id=table_ocid,
        update_row_details=oci.nosql.models.UpdateRowDetails(
            value={
                'tpc': f"{tpc}",
                'token': f"{token}"
            }
        )
    )

def get_zoom_tokens(tpc, zoom_sdk_key):

    current_time = int(time.time())

    headers = {
        'alg': 'HS256',
        'typ': 'JWT'
    }
    payload = {
        'app_key': 'fNmQihVKmlnHDAfbcusRV797kNNA5EInQYUB',
        'tpc': f'{tpc}',
        'version': 1,
        'role_type': 0,
        'iat': current_time,
        'exp': current_time + 7200
    }

    client_zoom_token = jwt.encode(payload, zoom_sdk_key, "HS256", headers)
    payload["role_type"] = 1
    admin_zoom_token = jwt.encode(payload, zoom_sdk_key, "HS256", headers)

    return [client_zoom_token, admin_zoom_token]