from django.http import JsonResponse
from . models import Leaderboard

# Create your views here.
def fetchleaderBoardResultForAll(request):
    if request.method == 'GET':
        try:
            leaderboardresult = Leaderboard.objects.all()

            if not leaderboardresult:
                return JsonResponse({'message':'No leaderboard result fetched'},status=400)
            
            serialiseddata = [
                {
                    'id' : item.user.id,
                    'name' : item.user.username,
                    'gameplayed' : item.user.total_game_played,
                    'rank' : item.rank,
                    'totalpoints' : item.points
                }
                for item in leaderboardresult
            ]
            
            return JsonResponse({'message':'fetched leaderboard result','data':serialiseddata},status=200)

        except Exception as e:
            return JsonResponse({'message':f'Failed to Fetch leaderboard result : {str(e)}'},status=500)
    else:
        return JsonResponse({'message':'Invalid Request'},status=500)