import os
import ssl
import io
import json
import logging
import hashlib
import hmac
import urllib.request
import oci
from fdk import response

SECRET_TOKEN = os.getenv("SECRET_TOKEN")
BUCKET_NAME_SPACE = os.getenv("BUCKET_NAME_SPACE")
BUCKET_NAME = os.getenv("BUCKET_NAME")

def handler(ctx, data: io.BytesIO = None):
    body = json.loads(data.getvalue())
    event_type = body.get("event", "")
    logging.getLogger().info(event_type)
    if event_type == "endpoint.url_validation":
        plain_token = body["payload"]["plainToken"]
        encrypted_token = hmac.new(bytes(SECRET_TOKEN, 'ascii'), bytes(
            plain_token, 'ascii'), hashlib.sha256).hexdigest()
        response_json = {
            "plainToken": plain_token,
            "encryptedToken": encrypted_token
        }
        return response.Response(
            ctx, response_data=json.dumps(response_json),
            headers={"Content-Type": "application/json"}
        )

    download_token = body['download_token']
    recording_files = body['payload']['object']['recording_files']

    ## The session_name was supposed to be the signage name, but it should be unique,
    session_name = body['payload']['object']['session_name']
    ## Function has a temporary area, allowing free read/write access.
    tmp_file_path = "/tmp/{}.mp4".format(session_name)

    audio_only_file = [
        x for x in recording_files if x['file_extension'] == "M4A"][0]
    download_url = audio_only_file['download_url']

    ## To download the file, you need a download token, set in the Authorization header.
    opener = urllib.request.build_opener()
    opener.addheaders = [('Content-Type', 'application/json'),
                         ('Authorization', 'Bearer: {}'.format(download_token))]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(download_url, tmp_file_path)

    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

    with open(tmp_file_path, "rb") as f:
        data = f.read()
        client.put_object(BUCKET_NAME_SPACE, BUCKET_NAME, "{}.mp4".format(session_name), data)

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Success"}),
        headers={"Content-Type": "application/json"}
    )
