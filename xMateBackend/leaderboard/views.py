from django.http import JsonResponse
from models import Leaderboard

# Create your views here.
def fetchleaderBoardResultForAll(request):
    if request.method == 'POST':
        try:
            leaderboardresult = Leaderboard.objects.get()

            if not leaderboardresult or not leaderboardresult.length == 0:
                return JsonResponse({'message':'No leaderboard result fetched'},status=400)
            
            return JsonResponse({'message':'fetched leaderboard result'},status=200)

        except Exception as e:
            return JsonResponse({'message':f'Failed to Fetch leaderboard result : {str(e)}'},status=500)
    else:
        return JsonResponse({'message':'Invalid Request'},status=500)