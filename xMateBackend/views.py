from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def firstUrl(request):
    if request.method == 'GET':
        try:
            return JsonResponse({'message':'Hey its xmate backend project'},status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message':f'Failed to check first url: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def checkHealth(request):
    if request.method == 'GET':
        try:
            return JsonResponse({'message':'Everything is alright'},status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'message':f'Issue here: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({'message':'Invalid Request'},status=status.HTTP_400_BAD_REQUEST)
