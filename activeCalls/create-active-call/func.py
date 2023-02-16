import io
import oci
import base64
import os
import json
import jwt
from fdk import response
from dotenv import load_dotenv
from datetime import datetime


'''
    This function creates an active call and returns a client zoom token
'''
def handler(ctx, data: io.BytesIO = None):

    load_dotenv()
    zoom_secret_ocid = os.getenv("ZOOM_SECRET_OCID")

    try:
        request_body = json.loads(data.getvalue())
        tpc = request_body.get("tpc")
        signageName = request_body.get("signageName")

    except Exception:
        msg = "mandatory field missing in request body"
        return response.Response(ctx, msg, status_code = 400)

    signer = oci.auth.signers.get_resource_principals_signer()
    zoom_sdk_key = get_secret(signer, zoom_secret_ocid)
    
    now = datetime.now()

    zoom_tokens = get_zoom_tokens(tpc, int(datetime.timestamp(now)), zoom_sdk_key)
    insert_in_table(signer=signer, tpc=tpc, token=zoom_tokens[1], \
        current_time=now.strftime("%Y-%m-%dT%H:%M:%S"), signageName=signageName)
    
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

def insert_in_table(signer, tpc, token, current_time, signageName):

    table_ocid = os.getenv("TABLE_OCID")

    nosql_client = oci.nosql.NosqlClient({}, signer=signer)
    nosql_client.update_row(
        table_name_or_id=table_ocid,
        update_row_details=oci.nosql.models.UpdateRowDetails(
            value={
                'tpc': f"{tpc}",
                'token': f"{token}",
                'creationTime': f"{current_time}",
                'signageName': f"{signageName}"
            }
        )
    )

def get_zoom_tokens(tpc, current_time, zoom_sdk_key):

    headers = {
        'alg': 'HS256',
        'typ': 'JWT'
    }
    payload = {
        'app_key': f'{os.getenv("APP_KEY")}',
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
    