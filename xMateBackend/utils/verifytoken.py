import jwt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def verifyToken(token):
    try:
        if not token:
            return JsonResponse({'message':'token not passed'},status=400)
        
        payload = jwt.decode(token,settings.PYJWTSECRETKEY,algorithms=['HS256'])

        if not payload:
            return JsonResponse({'message':'Invalid token passed ,Payload not present'},status=400)
        
        user_id = payload.get('id')
        user = User.objects.get(id=user_id)

        if not user:
            return JsonResponse({'message':'Invalis Id'},status=400)
        
        return user
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({'message':'token expired'},status=400) 
    
    except jwt.InvalidTokenError:
        return JsonResponse({'message':'Invalid token'},status=400)
    
    except User.DoesNotExist:
        return JsonResponse({'message':' User not found'},status=400)
    
    except Exception as e:
        return JsonResponse({'message':f'Issue in verifying {str(e)}'},status=500)