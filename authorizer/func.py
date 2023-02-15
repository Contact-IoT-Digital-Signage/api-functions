import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import io
import json
import logging

from fdk import response

cred = credentials.Certificate("firebase_admin_sdk_config.json")
firebase_admin.initialize_app(cred)


def handler(ctx, data: io.BytesIO = None):
    id_token = json.loads(data.getvalue())['data'].get('authorization', '')

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        return json.dumps({
            "active": True
        })
    except:
        return json.dumps({
            "active": False
        })
