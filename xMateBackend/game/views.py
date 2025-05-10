import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.protectedroute import protectedRoute
from . models import Game

# Create your views here.
@csrf_exempt
@protectedRoute
def createMatchbtwChallengers(request):
    if request.method == 'POST':
        try:
            # player 1 user id which will create the match and he is logged in 
            player1userid = request.userid

            if not player1userid:
                return JsonResponse({'message':'Un authorised user'},status=400)
            
            matchCreated = Game.objects.create(
                player_1 = player1userid,
            )

            if not matchCreated:
                return JsonResponse({'message':'failed to create match'},status=400)
            
            return JsonResponse({
                'message':'Match Created',
                'game_id' : matchCreated.game_id,
                'player_1' : matchCreated.player_1,
                'player_2' : matchCreated.player_2,
                'status' : matchCreated.status
            },status=201)

        except Exception as e:
            return JsonResponse({'message':f'Failed to create match btw challengerss: {str(e)}'},status=500)
    else :
        return JsonResponse({'message':'Invalid Request'},status=405)


# When someone click on the link then this function will run and add this user to that match 
@csrf_exempt
def player2joinmatch(request):
    if request.method == 'POST':
        try:
            player2userid = request.userid

            if not player2userid:
                return JsonResponse({'message':'Unauthorised User'},status=400)

            data = json.loads(request.body)
            game_id = data.get('game_id')

            if not game_id:
                return JsonResponse({'message':'game_id is needed'},status=400)
            
            checkifgameidexits = Game.objects.filter(game_id=game_id).exists()

            if not checkifgameidexits:
                return JsonResponse({'message':'Invalid game_id'},status=400)
            
            try:
                game = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return JsonResponse({'message': 'Game not found'}, status=404)
            
            if game.player_2:
                return JsonResponse({'message': 'This game is already full'}, status=400)
            
            if game.status == 'Player_2_Joined': 
                 return JsonResponse({'message': 'This game is no longer accepting players'}, status=400)
            
            game.player_2 = player2userid
            game.player_2_status = 'Player_2_Joined'
            game.status = 'In_Progess'
            game.save()
            
            return JsonResponse({'message':'Game state update after player 2 join match'},status=200)

        except Exception as e:
            return JsonResponse({'message':f'Failed to Join match as a opponent: {str(e)}'},status=500)
    else :
        return JsonResponse({'message':'Invalid Request'},status=405)

