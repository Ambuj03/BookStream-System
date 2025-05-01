from django.shortcuts import render, redirect
from bm_app.models import Distributor


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        
    def __call__(self, request):
        #skiing for anony users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
         #only allowing to certain urls

        if request.path.startswith('/admin/') or \
           request.path.startswith('/logout/') or \
           request.path.startswith('/static/') or \
           request.path == '/complete-profile/' :
            return self.get_response(request)
        
        #check if the user has complete distributor profile or not

        try:
            distributor = Distributor.objects.get(user = request.user)

            if not distributor.distributor_phonenumber or not distributor.temple :
                return redirect('complete_profile')
            
        except Distributor.DoesNotExist:
            #user doesnt have a dist profile yet

            if request.user.socialaccount_set.exists():
                return redirect('complete_profile')
            
        return self.get_response(request)