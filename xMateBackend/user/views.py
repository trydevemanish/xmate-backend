import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.generateAccesstoken import generateAccesstoken
from utils.protectedroute import protectedRoute
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework import status
from .serializers import UserSerializer

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

            print(data)

            if not username or not email or not password:
                return JsonResponse({'message':'Valid Field are required.'},status=status.HTTP_204_NO_CONTENT)
            
            userexits = User.objects.filter(email=email).exists()

            if userexits:
                return JsonResponse({'message':'User Already exits'},status=status.HTTP_200_OK)
            
            created_user = User.objects.create_user(username=username,email=email,password=password)

            if not created_user :
                return JsonResponse({'message':'Issue Ocuured While creating User'},status=status.HTTP_404_NOT_FOUND)
            
            serialiserUser = UserSerializer(created_user)

            return JsonResponse({
                    'message':'User Registered',
                    'data':serialiserUser.data
                },status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return JsonResponse({'message':f'Failed to create User: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else : 
        return JsonResponse({'message':'Invalid Register Request'},status=status.HTTP_400_BAD_REQUEST)
    

# Login User 
@csrf_exempt
def loginUser(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'message':'Invalid Feild'},status=status.HTTP_204_NO_CONTENT)
            
            exixtedUser = User.objects.get(email=email)

            if not exixtedUser:
                return JsonResponse({'message':'Email is not registerd'},status=status.HTTP_404_NOT_FOUND)
            
            if not check_password(password,exixtedUser.password):
                return JsonResponse({'message':'password did not match'},status=status.HTTP_401_UNAUTHORIZED)
            
            # generate access or refresh token 
            access_token,refresh_token = generateAccesstoken(exixtedUser.id)
            
            exixtedUser.refreshtoken = refresh_token
            exixtedUser.save()

            print(refresh_token)
            
            return JsonResponse({
                'message':'Login successfully',
                'access_token' :access_token,
                'refresh_token' : refresh_token
            },status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Failed to login User: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return JsonResponse({'message':'Invalid Login Request'},status=status.HTTP_400_BAD_REQUEST)


# Logout User 
@csrf_exempt
@protectedRoute
def logoutUser(request):
    if request.method == 'POST':
        try:

            userid = request.userid

            if not userid:
                return JsonResponse({'message':'Unauthoriised user'},status=400)
            
            user = User.objects.get(id=userid)

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
@protectedRoute
def fetchLoginUserdetail(request):
    pass
    

# update the user stats after winning 
@csrf_exempt
def updateStatsAfterWinning(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('userid')

            if not id:
                return JsonResponse({'message':'Id not present'},status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(id=id)

            if not user:
                return JsonResponse({'message':'Invalid Id user not found'},status=status.HTTP_404_NOT_FOUND)
            
            user.Update_stats(win=True)

            return JsonResponse({'message':'User Match Updated'},status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'message':f'Issue Occured Updatine User stats'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)


# update the user stats after loosing 
@csrf_exempt
def updateStatsAfterLoosing(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('userid')

            if not id:
                return JsonResponse({'message':'Id not present'},status=status.HTTP_404_NOT_FOUND)
            
            user = User.objects.get(id=id)

            if not user:
                return JsonResponse({'message':'Invalid Id user not found'},status=status.HTTP_404_NOT_FOUND)
            
            user.Update_stats(loss=True)

            return JsonResponse({'message':'User Match Updated'},status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'message':f'Issue Occured Updatine User stats'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)