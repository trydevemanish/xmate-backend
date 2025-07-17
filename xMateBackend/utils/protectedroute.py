from django.http import JsonResponse
from utils.verifytoken import verifyToken
from functools import wraps
from rest_framework import status

# defining a decorater to protect api route , takes a function as an input to protect 
def protectedRoute(view_func):
    @wraps(view_func)

    def wrapper(request, *args, **kwargs):
        if request.headers.get('Authorization'):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'message':'Authorization token note in header'},status=status.HTTP_404_NOT_FOUND)
            
            auth_token = auth_header.split(' ')[1]

            if not auth_token:
                return JsonResponse({'message':'Token not present'},status=status.HTTP_404_NOT_FOUND)
            
            # verifying token if it is valid or not 
            auth_token_strip = auth_token.strip()
            user_id = verifyToken(auth_token_strip)

            if user_id is None:
                return JsonResponse({'message':'User_id did not received from token'},status=status.HTTP_404_NOT_FOUND)
            
            request.userid = user_id
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
    

    