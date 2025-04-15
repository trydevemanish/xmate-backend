import json
from .models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils import generateAccesstoken
from django.contrib.auth import authenticate

# Register user 
@csrf_exempt
def registerUser(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not email or not password:
                return JsonResponse({'message':'Valid Field are required.'},status=400)
            
            userexits = User.objects.filter(email=email).exists()
            if userexits:
                return JsonResponse({'message':'User Already exits'},status=200)
            
            created_user = User.objects.create_user(username=username,email=email,password=password)

            if not created_user :
                return JsonResponse({'message':'Issue Ocuured While creating User'},status=400)
            
            return JsonResponse({'mesage':'User Created Successfully','data':created_user},status=201)
        
        except Exception as e:
            return JsonResponse({'message':f'Failed to create User: {str(e)}'},status=500)
    else : 
        return JsonResponse({'message':'Invalid Register Request'},status=405)
    

# Login User 
@csrf_exempt
def loginUser(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'message':'Invalid Feild'},status=400)
            
            exixtedUser = User.objects.filter(email=email).exists()
            
            if not exixtedUser:
                return JsonResponse({'message':'User Is not registerd'},status=200)
            
            user = authenticate(email=email, password=password)

            if user is None: 
                return JsonResponse({'message':'Invlid credentials passed'},status=404)
            
            # generate access or refresh token 

            access_token,refresh_token = generateAccesstoken(exixtedUser.id)

            User.refreshtoken = refresh_token
            User.save()

            return JsonResponse({
                'message':'User Login successfully',
                'access_token' :access_token,
                'refresh_token' : refresh_token
            },status=200)

        except Exception as e:
            return JsonResponse({'message':f'Failed to login User: {str(e)}'},status=500)
        
    return JsonResponse({'message':'Invalid Login Request'},status=405)
