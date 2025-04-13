from .models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

@csrf_exempt
def registerUser(request):
    # steps to register user 
    # 1 -> get the user detail 
    # 2- > check if user already exits or not 
    # 3- > if exxits send a message user exit 
    # 4-> if not create a new User 
    # 5-> send a message that show user created successfully
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not email or not password:
                return JsonResponse({'message':'Valid Field are required.'},status=400)
            
            userexits = User.objects.filter(username=username).exists()
            if userexits:
                return JsonResponse({'message':'User Already exits'},status=200)
            
            created_user = User.objects.create_user(username=username,email=email,password=password)

            if not created_user :
                return JsonResponse({'message':'Issue Ocuured While creating User'},status=400)
            
            return JsonResponse({'mesage':'User Created Successfully','data':created_user},status=201)
        except Exception as e:
            return JsonResponse({'message':str(e)},status=500)
    else : 
        return JsonResponse({'message':'Invalid Request'},status=405)