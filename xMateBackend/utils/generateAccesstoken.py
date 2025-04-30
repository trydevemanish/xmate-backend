import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse

def generateAccesstoken(userid):
    access_token_payload = {
        "id" : userid,
        'exp' : datetime.now() + timedelta(days=3),
        'iat': datetime.now(),
    }

    access_token = jwt.encode(access_token_payload, settings.PYJWTSECRETKEY,algorithm="HS256")

    if not access_token:
        return JsonResponse({'message':'Issue generating accesstoken.'},status=400)

    refresh_token_payload = {
        "id" : userid,
        'exp':datetime.now() + timedelta(days=3),
        'iat' : datetime.now()
    }

    refresh_token = jwt.encode(refresh_token_payload, settings.PYJWTSECRETKEY,algorithm="HS256")

    if not refresh_token:
        return JsonResponse({'message':'Issue generating refreshtoken'},status=400)
    
    return access_token, refresh_token 

