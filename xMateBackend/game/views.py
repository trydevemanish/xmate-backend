import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.protectedroute import protectedRoute
from . models import Game
from .serializers import GameSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
@csrf_exempt
@protectedRoute
def createMatchbtwChallengers(request):
    if request.method == 'POST':
        try:
            # player 1 user id the one who will create the match and he is logged in 
            player1userid = request.userid

            if not player1userid:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_instance = User.objects.get(id=player1userid)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # here we will check if user is any game 
            checkUserAlreadyExitsInAnyGame = Game.objects.get(
                player_1 = user_instance,
                game_status = 'pending' or 'in_progress'
            )

            # if yes then send a message 
            if checkUserAlreadyExitsInAnyGame:
                return JsonResponse({'message':'User is already in game'},status=status.HTTP_400_BAD_REQUEST)
            
            # if not then create a match 
            matchCreated = Game.objects.create(
                player_1 = user_instance,
            )

            if not matchCreated:
                return JsonResponse({'message':'failed to create match'},status=status.HTTP_400_BAD_REQUEST)
            
            gameMatchSerializer = GameSerializer(matchCreated)

            if not gameMatchSerializer:
                return JsonResponse({'message':'failed to serialise game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({
                'message':'Match Created',
                'data' : gameMatchSerializer.data
            },status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'message':f'Failed to create match btw challengers: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else :
        return JsonResponse({'message':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)


# When someone click on the link then this function will run and add this user to that match 
@csrf_exempt
def player2joinmatch(request):
    if request.method == 'POST':
        try:
            player2userid = request.userid

            if not player2userid:
                return JsonResponse({'message':'Unauthorised User'},status=status.HTTP_400_BAD_REQUEST)

            data = json.loads(request.body)
            game_id = data.get('game_id')

            if not game_id:
                return JsonResponse({'message':'game_id is needed'},status=status.HTTP_400_BAD_REQUEST)
            
            checkifgameidexits = Game.objects.filter(game_id=game_id).exists()

            if not checkifgameidexits:
                return JsonResponse({'message':'Invalid game_id'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                game = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return JsonResponse({'message': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            if game.player_2:
                return JsonResponse({'message': 'This game is already full'}, status=status.HTTP_400_BAD_REQUEST)
            
            if game.status == 'Player_2_Joined': 
                return JsonResponse({'message': 'This game is no longer accepting players'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                player_2_user_instance = User.objects.get(id=player2userid)
                if not player_2_user_instance or player_2_user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # here we will check if user is any game 
            checkUserAlreadyExitsInAnyGame = Game.objects.get(
                player_2 = player_2_user_instance,
                game_status = 'pending' or 'in_progress'
            )

            # if yes then send a message 
            if checkUserAlreadyExitsInAnyGame:
                return JsonResponse({'message':'User is already in game'},status=status.HTTP_400_BAD_REQUEST)
            
            game.player_2 = player_2_user_instance
            game.player_2_status = 'Player_2_Joined'
            game.status = 'In_Progess'
            game.save()
            
            return JsonResponse({'message':'Game state update after player 2 join match','notify' : 'player 2 joined'},status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'message':f'Failed to Join match as a opponent: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else :
        return JsonResponse({'message':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)

