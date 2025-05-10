import json
from django.shortcuts import render
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

