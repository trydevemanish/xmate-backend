from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid

# Create your views here.
@csrf_exempt
def createMatchbtwChallengers(request):
    if request.method == 'POST':
        try:
            userid = request.user._id

            if not userid:
                return JsonResponse({'message':'Un authorised user'},status=400)
            
            

        except Exception as e:
            return JsonResponse({'message':f'Failed to create match btw challengerss: {str(e)}'},status=500)
    else :
        return JsonResponse({'message':'Invalid Request'},status=405)

