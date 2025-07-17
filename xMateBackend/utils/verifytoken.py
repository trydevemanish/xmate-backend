import jwt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

def verifyToken(token):
    try:
        if not token:
            return JsonResponse({'message':'token not passed'},status=status.HTTP_404_NOT_FOUND)
        
        payload = jwt.decode(token, settings.PYJWTSECRETKEY, algorithms=["HS256"])

        if not payload:
            return JsonResponse({'message':'Invalid token passed ,Payload not present'},status=status.HTTP_404_NOT_FOUND)
        
        user_id = payload.get('id')

        if not user_id:
            return JsonResponse({'message':'User id not present in payload'},status=status.HTTP_404_NOT_FOUND)

        user = User.objects.get(id=user_id)

        if not user:
            return JsonResponse({'message':'Invalis userid in payload'},status=status.HTTP_404_NOT_FOUND)
        
        return user_id
    
    except jwt.ExpiredSignatureError:
        print('token expired')
        return JsonResponse({'message':'token expired'},status=status.HTTP_404_NOT_FOUND) 
    
    except jwt.InvalidTokenError:
        print('invalid token')
        return JsonResponse({'message':'Invalid token'},status=status.HTTP_404_NOT_FOUND)
    
    except User.DoesNotExist:
        print('user does not exist')
        return JsonResponse({'message':' User not found'},status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        print('other exception:', str(e))
        return JsonResponse({'message':f'Issue in verifying {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)