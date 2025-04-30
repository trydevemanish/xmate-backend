from django.http import JsonResponse
from utils import verifytoken
from functools import wraps

def protectedRoute(view_func):
    @wraps(view_func)

    def wrapper(request, *args, **kwargs):
        if request.headers.get('Authorization'):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'message':'Unauthorised User'},status=400)
            
            auth_token = auth_header.split(' ')[1]

            if not auth_token:
                return JsonResponse({'message':'Token not present'},status=400)
            
            # verifying token if it is valid or not 
            user = verifytoken.verifyToken(auth_token)

            if user is None:
                return JsonResponse({'message':'User is empty'},status=400)
            
            request.userid = user.id
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
    

    