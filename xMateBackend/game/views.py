import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.protectedroute import protectedRoute
from . models import Game
from .serializers import GameSerializer
from rest_framework import status
from django.db.models import Q
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
            checkUserAlreadyExitsInAnyGame = Game.objects.filter(
                player_1 = user_instance,
                game_status = 'pending' or 'in_progress'
            ).exists()

            # if yes then send a message 
            if checkUserAlreadyExitsInAnyGame:
                return JsonResponse({'message':'you are already in a game'},status=status.HTTP_200_OK)
            
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
@protectedRoute
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

            print('checkifgameidexits',checkifgameidexits)

            if not checkifgameidexits:
                return JsonResponse({'message':'Invalid game_id'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                game = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return JsonResponse({'message': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            if game.player_2:
                return JsonResponse({'message': 'This game is already full'}, status=status.HTTP_400_BAD_REQUEST)
            
            if game.game_status == 'Player_2_Joined': 
                return JsonResponse({'message': 'This game is no longer accepting players'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                player_2_user_instance = User.objects.get(id=player2userid)
                if not player_2_user_instance or player_2_user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            print('game and user instance had found here')
            
            # here we will check if user is any game 
            checkUserAlreadyExitsInAnyGame = Game.objects.filter(
                player_2 = player_2_user_instance,
                game_status = 'pending' or 'in_progress'
            ).exists()

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


# check if 2nd user has joined the match 
@csrf_exempt
def checkifPlayer_2_hasJoinedGame(request):
    if request.method == 'POST':
        try:
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
            
            # checking if player2 has joined or not 
            checkifPlayer_2_has_joined = game.objects.exists(
                player_2_status='player_2_joined'
            )

            if not checkifPlayer_2_has_joined:
                return JsonResponse({'message': 'player_2_has_not_joined_yet'}, status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message': 'player_2_has_joined'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message':f'Failed to Join match as a opponent: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)
    

# this will tell all the game created by the user that are in the pending or inprogess remember it will only tell the game that user has created as the player_1 not the game user joined as the player_2  
@csrf_exempt
@protectedRoute
def finding_user_pending_or_inprogess_games(request):
    if request.method == 'GET':
        try:
            userid = request.userid

            if not userid:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_instance = User.objects.get(id=userid)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)

            all_the_games_user_created_as_player_1 = Game.objects.get(
                player_1=user_instance,
                game_status='pending' or 'in_progress'
            )

            if not all_the_games_user_created_as_player_1:
                return JsonResponse({'message':'No game is pending'},status=status.HTTP_200_OK)
            
            all_the_games_user_created_as_player_1_serialised_data = GameSerializer(all_the_games_user_created_as_player_1)

            if not all_the_games_user_created_as_player_1_serialised_data:
                return JsonResponse({'message':'Issue Occured while serialising game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message':'All pending game found','data':all_the_games_user_created_as_player_1_serialised_data.data},status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Failed to find user pending game match: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)


# finding two games either user created or joined a match created by another game 
@csrf_exempt
@protectedRoute
def finding_user_recent_two_games(request):
    if request.method == 'GET':
        try:
            userid = request.userid

            if not userid:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_instance = User.objects.get(id=userid)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return JsonResponse({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)
            
            two_recent_game_played_by_user = Game.objects.filter(
                (Q(player_1=user_instance) | Q(player_2=user_instance)) &
                Q(player_1__isnull=False)
            ).order_by('-created_at')[:2]

            if not two_recent_game_played_by_user:
                return JsonResponse({'message':'User have not joined any game'},status=status.HTTP_404_NOT_FOUND)
            
            two_recent_game_played_by_user_serialised_data = GameSerializer(two_recent_game_played_by_user,many=True)

            if not two_recent_game_played_by_user_serialised_data:
                return JsonResponse({'message':'Issue Occured while serialising game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message':'found two recent game','data':two_recent_game_played_by_user_serialised_data.data},status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Failed to find user pending game match: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)


# deleting a game would lead to decrese the ranking and other detail of the user like total game played ect .. only when game status is completed
@csrf_exempt
@protectedRoute
def delete_a_game(request):
    if request.method == 'DELETE':
        try:
            userid = request.userid

            if not userid:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_instance = User.objects.get(id=userid)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)
            
            data = json.loads(request.body)
            game_id = data.get('game_id')

            if not game_id:
                return JsonResponse({'message':'game_id is needed'},status=status.HTTP_400_BAD_REQUEST)
            
            checkifgameidexits = Game.objects.filter(game_id=game_id).exists()

            if not checkifgameidexits:
                return JsonResponse({'message':'Invalid game_id'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                game_instance = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return JsonResponse({'message': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # steps need to do 
            if game_instance.player_1 != user_instance:
                return JsonResponse({'message':'you cannot delete the game only the match creater can delete'},status=status.HTTP_400_BAD_REQUEST)
            
            game_instance.delete()

            return JsonResponse({'message':'Game deleted'},status=status.HTTP_204_NO_CONTENT)
            # if game.status is completed than if game is deleted than only we need to make changes to the user_instance 
            

        except Exception as e:
            return JsonResponse({'message':f'Failed to find user pending game match: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def fetchGameData(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            game_id = data.get('game_id')

            if not game_id:
                return JsonResponse({'message':'game_id is needed'},status=status.HTTP_400_BAD_REQUEST)
            
            checkifgameidexits = Game.objects.filter(game_id=game_id).exists()

            if not checkifgameidexits:
                return JsonResponse({'message':'Invalid game_id'},status=status.HTTP_200_OK)
            
            try:
                game_instance = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return JsonResponse({'message': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            serialised_game_instance = GameSerializer(game_instance)

            if not serialised_game_instance:
                return JsonResponse({'message':'Issue Occured while serialising game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message':'found game instance data','data':serialised_game_instance.data},status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'message':f'Failed to find specific gamedata: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)


# this function will find all the games in which user is involved as player1 or player2 or if the game status is pending or completed 
@csrf_exempt
@protectedRoute
def find_game_in_which_userisinvolved_can_be_pendingorcompleted(request):
    if request.method == 'GET':
        try:
            userid = request.userid

            if not userid:
                return JsonResponse({'message':'UnAuthorised user'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user_instance = User.objects.get(id=userid)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)
            
            recent_games_user_is_invloved = Game.objects.filter(
                (Q(player_1=user_instance) | Q(player_2=user_instance)) &
                Q(player_1__isnull=False),
            ).order_by('-created_at')

            if not recent_games_user_is_invloved:
                return JsonResponse({'message':'User is not invloved in any game'},status=status.HTTP_404_NOT_FOUND)
            
            recent_game_user_isInvloved_serialised_data = GameSerializer(recent_games_user_is_invloved,many=True)

            if not recent_game_user_isInvloved_serialised_data:
                return JsonResponse({'message':'Issue Occured while serialising game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message':'found recent game user is involved','data':recent_game_user_isInvloved_serialised_data.data},status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Failed to find game user is involved: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)
    


# finding games in which game status is pending or and player 2 status is null 
@csrf_exempt
def findingGameswhosestatusis_Pending(request):
    if request.method == 'POST':
        try:
            
            games_to_join = Game.objects.filter(
                Q(game_status='pending' or 'in_progress') & Q(player_2_status='player_2_not_joined')
            ).order_by('-created_at')

            if not games_to_join:
                return JsonResponse({'message':'No'},status=status.HTTP_404_NOT_FOUND)
            
            games_to_join_serialised_data = GameSerializer(games_to_join,many=True)

            if not games_to_join_serialised_data:
                return JsonResponse({'message':'Issue Occured while serialising game data'},status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'message':'found games','data':games_to_join_serialised_data.data},status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'message':f'Failed to find game: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def UpdateGameStatsAfterWinning(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('userid')
            gameid = data.get('gameid')

            if not id or not gameid:
                return JsonResponse({'message':'Id not present'},status=status.HTTP_404_NOT_FOUND)
            
            try:
                user_instance = User.objects.get(id=id)
                if not user_instance or user_instance is None:
                    return JsonResponse({'message':'user id is not valid'},status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)
            
            game_instance = Game.objects.filter(game_id=gameid).first

            if not game_instance:
                return JsonResponse({'message': 'game instance is not valid'},status=status.HTTP_404_NOT_FOUND)
            
            game_instance.end_game(winner=user_instance)
            return JsonResponse({'message':'game stats updated success'},status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({'message':f'Issue Occured Updatine User stats'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid request'},status=status.HTTP_400_BAD_REQUEST)
# needs to handle these routes 
# fetch recent 2 games of login user - done
# fetch games of the login user that are pending or in progress - done
# fetch games user is involved in it can be complete or pending 
# fetch some games whose status is pending 
# if the game is not completed but you still need to create a new game due to any issue like player 2 is not avialabel or not want to complete the match etc in that case you can probably delete that game match and create a new game