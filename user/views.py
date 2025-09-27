import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.generateAccesstoken import generateAccesstoken
from utils.protectedroute import protectedRoute
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework import status
from .serializers import UserSerializer
from game.models import Game
from django.db.models import Q
from django.utils import timezone

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

            response = JsonResponse({
                'message':'Login successfully',
                'access_token' :access_token,
                'refresh_token' : refresh_token
            })

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,            # Only over HTTPS
                samesite='Strict',      # or 'Lax' depending on your use case
                max_age=7 * 24 * 60 * 60  # e.g. 7 days
            )
            
            return response

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
    if request.method == 'GET':
        try:
            id = request.userid

            if type(id) != int:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_401_UNAUTHORIZED)
            
            user = User.objects.get(id=id)

            if not user:
                return JsonResponse({'message':'Invalid Id user not found'},status=status.HTTP_404_NOT_FOUND)
            
            serialisedUser = UserSerializer(user)
            
            return JsonResponse({'message':'User Data','data':serialisedUser.data},status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'message':f'Issue Occured fetching User detail'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else : 
        return JsonResponse({'message':'Invalid request'},status=405)


@csrf_exempt
def fetchAllUserForPlayerRank(request):
    if request.method == 'GET':
        try:
            allUser = User.objects.all()
            leaderboard_data = []

            for user in allUser:
                total_games = user.total_game_played
                wins = user.total_game_win
                losses = user.total_game_losses

                # this will be count only for the ones who has played more than 10 matches cux if a new user come and play it eould show him as th top 
                winrate = (wins / total_games) if total_games > 0 else 0
                recent_user_game = Game.objects.filter(
                    (Q(player_1=user.id) | Q(player_2=user.id)) &
                    Q(player_1__isnull=False)
                ).order_by('-created_at')[:1]

                recent_user_game_date = list(recent_user_game)[0].created_at

                if recent_user_game_date:
                    days_ago = (timezone.now() - recent_user_game_date).days
                    recent_score = max(0, 30 - days_ago) 
                else:
                    recent_score = 0

                leaderboard_score = (
                    (winrate * 0.3) + 
                    (user.total_points * 0.4) +
                    (total_games * 0.2) +
                    (recent_score * 0.1) 
                )

                leaderboard_data.append({
                    "id": user.id,
                    "username": user.username,
                    "email" : user.email,
                    "total_game_played": total_games,
                    "total_game_win": wins,
                    "total_game_losses": losses,
                    "total_game_draw": user.total_game_draw,
                    "total_points": user.total_points,
                    "win_rate": round(winrate, 2),
                    "leaderboard_score": round(leaderboard_score, 2),
                    "recent_game_played" : days_ago
                })

            leaderboard_sorted = sorted(leaderboard_data, key=lambda x: x["leaderboard_score"], reverse=True)

            if not allUser:
                return JsonResponse({'message':'Issue Ocuured while fetching All User'},status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'message':'Fetched all User Data','data':leaderboard_sorted}, safe=False,status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Issue Occured fetching Rank detail: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else : 
        return JsonResponse({'message':'Invalid request'},status=405)
    
