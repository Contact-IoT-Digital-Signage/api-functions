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

# Retrieve secret
def get_secret(secret_client, secret_ocid):
    
    secret = secret_client.get_secret_bundle(secret_ocid).data.secret_bundle_content.content.encode('utf-8')
    decrypted_secret = base64.b64decode(secret).decode("utf-8")
    return decrypted_secret

def handler(ctx, data: io.BytesIO = None):

    load_dotenv()
    SECRETS_OCID = os.getenv("SECRETS_OCID")

    signer = oci.auth.signers.get_resource_principals_signer()
    secret_client = oci.secrets.SecretsClient({}, signer=signer)    
    ZOOM_VIDEO_SDK_SECRET = get_secret(secret_client, SECRETS_OCID)

    headers = {
        'alg': 'HS256',
        'typ': 'JWT'
    }
    current_time = int(time.time())
    payload = {
        'app_key': 'fNmQihVKmlnHDAfbcusRV797kNNA5EInQYUB',
        'tpc': 'MYTOPIC',
        'version': 1,
        'role_type': 0,
        'iat': current_time,
        'exp': current_time + 7200
    }

    encoded_jwt = jwt.encode(payload, ZOOM_VIDEO_SDK_SECRET, "HS256", headers)
    
    return response.Response(
        ctx, response_data=json.dumps(
            {"token": f"{encoded_jwt}"}),
        headers={"Content-Type": "application/json"}
    )
