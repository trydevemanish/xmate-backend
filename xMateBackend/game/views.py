import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.protectedroute import protectedRoute

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
            
             

        except Exception as e:
            return JsonResponse({'message':f'Failed to create match btw challengerss: {str(e)}'},status=500)
    else :
        return JsonResponse({'message':'Invalid Request'},status=405)

