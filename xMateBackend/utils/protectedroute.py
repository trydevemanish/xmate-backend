from django.http import JsonResponse
from utils import verifytoken

def protectedRoute(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'message':'Unauthorised User'},status=400)
    
    auth_token = auth_header.split(' ')[1]

    if not auth_token:
        return JsonResponse({'message':'Token not present'},status=400)
    
    user = verifytoken(auth_token)

    if user is None:
        return JsonResponse({'message':'User is empty'},status=400)
    
    return JsonResponse({'message':''})
    

    
