from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Distributor
from django.contrib.auth.models import User
from .forms import DistributorProfileForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

#For password reset
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.utils.decorators import method_decorator



@login_required
@never_cache
def profile_dashboard(request):
    return render(request, 'bm_app/profile_temps/profile_dashboard.html')

@login_required
@never_cache
def view_profile(request):
    user = User.objects.get(id = request.user.id)
    distributor = Distributor.objects.get(user = request.user)

    context = {
        'user' : user,
        'distributor' : distributor,
    }

    return render(request, 'bm_app/profile_temps/view_profile.html', context)
    

@login_required
@never_cache
def edit_profile(request):
    distributor = Distributor.objects.get(user=request.user)    
    if request.method == 'POST':
        form = DistributorProfileForm(request.POST, instance=distributor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
    else:
        form = DistributorProfileForm(instance=distributor)

    # Adding boots classes, could be addedin html too
    for field_name, field in form.fields.items():
        field.widget.attrs['class'] = 'form-control'
    
    context = {
        'form': form,
        'distributor': distributor,
    }
    
    return render(request, 'bm_app/profile_temps/edit_profile.html', context)

@login_required
@never_cache
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            #Updating the session to prevent logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            # request.session.save()
            return redirect('profile_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    # Adding boots classes, could be addedin html too
    for field_name, field in form.fields.items():
        field.widget.attrs['class'] = 'form-control'
    
    context = {'form': form}
    return render(request, 'bm_app/profile_temps/change_password.html', context)


# Password Reset Stuff
@method_decorator(never_cache, name='dispatch')
class ResetPasswordView(PasswordResetView):
    template_name = 'bm_app/pass_reset/password_reset.html'
    email_template_name = 'bm_app/pass_reset/password_reset_email.html'
    subject_template_name = 'bm_app/pass_reset/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
