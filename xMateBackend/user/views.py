import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils import generateAccesstoken
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model

User = get_user_model()

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
            
            return JsonResponse({
                    'mesage':'User Created Successfully',
                    "id": created_user.id,
                    "username": created_user.username,
                    "email": created_user.email,
                    "hashedPaswordindb" : created_user.password,
                }, status=201
            )
        
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
            
            exixtedUser = User.objects.get(email=email)

            if not exixtedUser:
                return JsonResponse({'message':'Email is not registerd'},status=200)
            
            
            if not check_password(password,exixtedUser.password):
                return JsonResponse({'message':'password did not match'},status=404)
            
            # generate access or refresh token 
            access_token,refresh_token = generateAccesstoken.generateAccesstoken(exixtedUser.id)

            print("token geneatated : access_token",access_token)
            print("token geneatated : refresh_token",refresh_token)

            exixtedUser.refreshtoken = refresh_token
            exixtedUser.save()

            return JsonResponse({
                'message':'User Login successfully',
                'access_token' :access_token,
                'refresh_token' : refresh_token
            },status=200)

        except Exception as e:
            return JsonResponse({'message':f'Failed to login User: {str(e)}'},status=500)
        
    return JsonResponse({'message':'Invalid Login Request'},status=405)


# Logout User 
@csrf_exempt
def logoutUser(request):
    if request.method == 'POST':
        try:

            userid = request.user.id

            if not userid:
                return JsonResponse({'message':'Unauthoriised user'},status=400)
            
            user = User.objects.filter(id=userid).first()

            if not user:
                return JsonResponse({'message':'Invalid Id user not found'},status=400)
            
            user.refreshtoken = None
            user.save()

            return JsonResponse({'message':'User logout'},status=200)

        except Exception as e:
            return JsonResponse({'message':f'Issue Occured in logout user {str(e)}'},status=400)
    else : 
        return JsonResponse({'message':'Invalid request'},status=405)
    

# fetch User detail 
@csrf_exempt
def fetchLoginUserdetail(request):

    if request.method == 'GET':
        try:
            userid = request.user.id

            if not userid:
                return JsonResponse({'message':'Unauthoriised user'},status=400)
            
            user = User.objects.filter(id=userid).first()

            if not user:
                return JsonResponse({'message':'Invalid Id user not found'},status=400)
            
            return JsonResponse({'message':'User Data','Data':user},status=200)
            
        except Exception as e:
            return JsonResponse({'message':f'Issue Occured fetching User detail'},status=500)
    else:
        return JsonResponse({'message':'Invalid request'},status=405)
    
    