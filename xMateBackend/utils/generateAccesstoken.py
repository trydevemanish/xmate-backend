import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status

def generateAccesstoken(userid):
    access_token_payload = {
        "id" : userid,
        'exp' : (datetime.now(timezone.utc) + timedelta(days=4)).timestamp(),
        'iat':datetime.now(timezone.utc).timestamp(),
    }

    access_token = jwt.encode(access_token_payload, settings.PYJWTSECRETKEY,algorithm="HS256")

    if not access_token:
        return JsonResponse({'message':'Issue generating accesstoken.'},status=status.HTTP_404_NOT_FOUND)

    refresh_token_payload = {
        "id" : userid,
        'exp' : (datetime.now(timezone.utc) + timedelta(days=7)).timestamp(),
        'iat':datetime.now(timezone.utc).timestamp(),
    }

    refresh_token = jwt.encode(refresh_token_payload, settings.PYJWTSECRETKEY,algorithm="HS256")

    if not refresh_token:
        return JsonResponse({'message':'Issue generating refreshtoken'},status=status.HTTP_404_NOT_FOUND)
    
    return access_token, refresh_token 

